"""
Streamlit user interface for the multi‑tenant diary platform.

This front‑end authenticates against the FastAPI backend and allows users to
create and browse notes, perform semantic search and manage tasks.  It uses
Streamlit’s session state to persist authentication tokens between requests.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import requests
import streamlit as st


# Backend base URL (update if running on a different host/port)
# In Docker, use service name; locally, use localhost
API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")


def api_post(endpoint: str, data: dict, token: Optional[str] = None) -> requests.Response:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    # Use json parameter instead of data=json.dumps() for proper JSON encoding
    return requests.post(f"{API_BASE_URL}{endpoint}", json=data, headers=headers)


def api_get(endpoint: str, params: dict | None = None, token: Optional[str] = None) -> requests.Response:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.get(f"{API_BASE_URL}{endpoint}", params=params, headers=headers)


def api_put(endpoint: str, data: dict, token: Optional[str] = None) -> requests.Response:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    # Use json parameter instead of data=json.dumps() for proper JSON encoding
    return requests.put(f"{API_BASE_URL}{endpoint}", json=data, headers=headers)


def api_delete(endpoint: str, token: Optional[str] = None) -> requests.Response:
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.delete(f"{API_BASE_URL}{endpoint}", headers=headers)


def login(tenant_id: str, username: str, password: str) -> Dict[str, str] | None:
    """Login and return tokens. Shows error message on failure."""
    if not tenant_id or not username or not password:
        st.error("⚠️ All fields are required")
        return None
    
    try:
        resp = api_post("/auth/login", {"tenant_id": tenant_id, "username": username, "password": password})
        if resp.status_code == 200:
            return resp.json()
        else:
            # Try to get error details
            try:
                error_data = resp.json()
                error_detail = error_data.get('detail', 'Unknown error')
            except:
                error_detail = f"HTTP {resp.status_code}: {resp.text[:100]}"
            
            st.error(f"❌ Login failed: {error_detail}")
            if "Incorrect username or password" in error_detail:
                st.info("💡 Tip: Make sure you're using the correct Tenant ID, username, and password.")
            return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Connection error: Unable to reach the backend. Please check if the service is running.")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None


def load_notes(token: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[dict]:
    """Load notes with optional date filtering. Returns empty list on error."""
    try:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        resp = api_get("/notes/", params=params, token=token)
        if resp.status_code == 200:
            return resp.json()
        else:
            if resp.status_code == 401:
                st.error("Session expired. Please log in again.")
                st.session_state["auth"] = {}
                st.rerun()
            return []
    except Exception:
        return []


def create_note(token: str, tenant_id: str, user_id: str, title: str, content: str, tags: List[str]) -> None:
    """Create a new note. Shows success/error messages."""
    if not content.strip():
        st.warning("⚠️ Note content cannot be empty!")
        return
    
    payload = {
        "tenant_id": tenant_id,
        "user_id": user_id,
        "title": title,
        "content": content,
        "tags": tags,
    }
    try:
        resp = api_post("/notes/", payload, token=token)
        if resp.status_code == 201:
            st.success("✅ Note created successfully!")
            st.rerun()
        elif resp.status_code == 401:
            st.error("Session expired. Please log in again.")
            st.session_state["auth"] = {}
            st.rerun()
        else:
            error_msg = resp.json().get('detail', 'Unknown error') if resp.status_code != 500 else 'Server error'
            st.error(f"❌ Failed to create note: {error_msg}")
    except Exception as e:
        st.error(f"❌ Connection error: Unable to create note. Please try again.")


def update_note(token: str, note_id: str, title: Optional[str] = None, content: Optional[str] = None, tags: Optional[List[str]] = None) -> None:
    """Update an existing note. Shows success/error messages."""
    payload = {}
    if title is not None:
        payload["title"] = title
    if content is not None:
        payload["content"] = content
    if tags is not None:
        payload["tags"] = tags
    
    try:
        resp = api_put(f"/notes/{note_id}", payload, token=token)
        if resp.status_code == 200:
            st.success("✅ Note updated successfully!")
            st.rerun()
        elif resp.status_code == 401:
            st.error("Session expired. Please log in again.")
            st.session_state["auth"] = {}
            st.rerun()
        else:
            error_msg = resp.json().get('detail', 'Unknown error') if resp.status_code != 500 else 'Server error'
            st.error(f"❌ Failed to update note: {error_msg}")
    except Exception:
        st.error("❌ Connection error: Unable to update note. Please try again.")


def delete_note(token: str, note_id: str) -> None:
    """Delete a note. Shows success/error messages."""
    try:
        resp = api_delete(f"/notes/{note_id}", token=token)
        if resp.status_code == 204:
            st.success("✅ Note deleted successfully!")
            st.rerun()
        elif resp.status_code == 401:
            st.error("Session expired. Please log in again.")
            st.session_state["auth"] = {}
            st.rerun()
        else:
            error_msg = resp.json().get('detail', 'Unknown error') if resp.status_code != 500 else 'Server error'
            st.error(f"❌ Failed to delete note: {error_msg}")
    except Exception:
        st.error("❌ Connection error: Unable to delete note. Please try again.")


def search_notes(
    token: str, 
    query: str, 
    top_k: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tags: Optional[str] = None,
    keyword_search: bool = False,
) -> Dict[str, any]:
    """Perform semantic search with optional filters. Returns empty dict on error."""
    if not query.strip():
        return {}
    
    params = {"q": query, "top_k": top_k}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    if tags:
        params["tags"] = tags
    if keyword_search:
        params["keyword_search"] = "true"
    
    try:
        resp = api_get("/search/", params=params, token=token)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 401:
            st.error("Session expired. Please log in again.")
            st.session_state["auth"] = {}
            st.rerun()
            return {}
        elif resp.status_code == 429:
            st.error("⚠️ Rate limit exceeded. Please wait a moment and try again.")
            return {}
        else:
            error_msg = resp.json().get('detail', 'Search failed') if resp.status_code != 500 else 'Server error'
            st.warning(f"⚠️ Search error: {error_msg}")
            return {}
    except Exception:
        st.error("❌ Connection error: Unable to perform search. Please try again.")
        return {}


def load_tasks(token: str, status_filter: Optional[str] = None) -> List[dict]:
    """Load tasks with optional status filter. Returns empty list on error."""
    try:
        params = {"status": status_filter} if status_filter else {}
        resp = api_get("/tasks/", params=params, token=token)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 401:
            st.error("Session expired. Please log in again.")
            st.session_state["auth"] = {}
            st.rerun()
            return []
        else:
            return []
    except Exception:
        return []


def complete_task(token: str, task_id: str) -> None:
    """Mark a task as completed. Shows success/error messages."""
    try:
        resp = api_post(f"/tasks/{task_id}/complete", {}, token=token)
        if resp.status_code == 200:
            st.success("✅ Task marked as completed!")
            st.rerun()
        elif resp.status_code == 401:
            st.error("Session expired. Please log in again.")
            st.session_state["auth"] = {}
            st.rerun()
        else:
            error_msg = resp.json().get('detail', 'Unknown error') if resp.status_code != 500 else 'Server error'
            st.error(f"❌ Failed to complete task: {error_msg}")
    except Exception:
        st.error("❌ Connection error: Unable to complete task. Please try again.")


def main() -> None:
    st.set_page_config(page_title="Diary Assistant", page_icon="📝")
    st.title("📘 Multi‑Tenant Digital Diary Platform")

    # Initialize session state
    if "auth" not in st.session_state:
        st.session_state["auth"] = {}

    # Show login form if not authenticated
    if not st.session_state["auth"]:
        st.subheader("🔐 Login")
        
        # Helper text
        with st.expander("ℹ️ Need help?"):
            st.write("**Default Test Credentials:**")
            st.code("Tenant ID: 11fe6fce-f50e-441d-942b-8d6becfbd7c0\nUsername: admin\nPassword: admin123")
        
        tenant_id = st.text_input("Tenant ID", placeholder="Enter your tenant UUID")
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        if st.button("🔐 Login", type="primary"):
            # Validate inputs
            if not tenant_id or not tenant_id.strip():
                st.error("⚠️ Please enter a Tenant ID")
            elif not username or not username.strip():
                st.error("⚠️ Please enter a username")
            elif not password or not password.strip():
                st.error("⚠️ Please enter a password")
            else:
                # Show loading state
                with st.spinner("Logging in..."):
                    tokens = login(tenant_id.strip(), username.strip(), password)
                    if tokens:
                        st.session_state["auth"] = {
                            "access_token": tokens["access_token"],
                            "refresh_token": tokens.get("refresh_token"),
                            "tenant_id": tenant_id.strip(),
                            "username": username.strip(),
                        }
                        st.success("✅ Login successful!")
                        st.rerun()
        return

    # Authenticated: display navigation
    access_token = st.session_state["auth"]["access_token"]
    tenant_id = st.session_state["auth"]["tenant_id"]
    username = st.session_state["auth"]["username"]

    st.sidebar.write(f"Signed in as {username} (Tenant {tenant_id})")
    page = st.sidebar.selectbox("Navigate", ["Dashboard", "Diary", "Search", "Tasks"])
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"auth": {}}))

    if page == "Dashboard":
        st.header("📊 Dashboard")
        
        # Load data
        with st.spinner("Loading dashboard data..."):
            notes = load_notes(access_token)
            tasks = load_tasks(access_token)
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        num_notes = len(notes)
        num_tasks = len(tasks)
        open_tasks = len([t for t in tasks if t.get("status") == "open"])
        completed_tasks = len([t for t in tasks if t.get("status") == "completed"])
        
        with col1:
            st.metric("📝 Total Notes", num_notes)
        with col2:
            st.metric("✅ Total Tasks", num_tasks)
        with col3:
            st.metric("🔄 Open Tasks", open_tasks)
        with col4:
            st.metric("✔️ Completed Tasks", completed_tasks)
        
        if num_tasks > 0:
            completion_rate = (completed_tasks / num_tasks) * 100
            st.progress(completion_rate / 100, text=f"Task Completion Rate: {completion_rate:.1f}%")
        
        st.divider()
        
        # Charts Section
        if notes or tasks:
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.subheader("📈 Note Activity Over Time")
                if notes:
                    df_notes = pd.DataFrame(notes)
                    df_notes["created_at"] = pd.to_datetime(df_notes["created_at"])
                    
                    # Group by different time periods
                    time_period = st.selectbox("View by", ["Daily", "Weekly", "Monthly"], key="note_time_period")
                    
                    if time_period == "Daily":
                        df_notes["period"] = df_notes["created_at"].dt.date
                    elif time_period == "Weekly":
                        df_notes["period"] = df_notes["created_at"].dt.to_period("W").astype(str)
                    else:  # Monthly
                        df_notes["period"] = df_notes["created_at"].dt.to_period("M").astype(str)
                    
                    freq = df_notes.groupby("period").size()
                    st.line_chart(freq)
                else:
                    st.info("No notes yet. Create your first note to see activity!")
            
            with chart_col2:
                st.subheader("📋 Task Status Breakdown")
                if tasks:
                    task_df = pd.DataFrame(tasks)
                    status_counts = task_df["status"].value_counts()
                    st.bar_chart(status_counts)
                else:
                    st.info("No tasks yet. Tasks are automatically extracted from your notes!")
        
        # Tags Analysis
        if notes:
            st.divider()
            st.subheader("🏷️ Top Tags")
            all_tags = []
            for note in notes:
                note_tags = note.get("tags", [])
                if note_tags:
                    all_tags.extend(note_tags)
            
            if all_tags:
                from collections import Counter
                tag_counts = Counter(all_tags)
                top_tags = dict(tag_counts.most_common(10))
                
                # Display as columns
                tag_cols = st.columns(min(5, len(top_tags)))
                for idx, (tag, count) in enumerate(top_tags.items()):
                    with tag_cols[idx % 5]:
                        st.metric(tag, count)
            else:
                st.info("No tags yet. Add tags to your notes to see them here!")
        
        # Recent Activity
        st.divider()
        st.subheader("🕐 Recent Activity")
        
        recent_col1, recent_col2 = st.columns(2)
        
        with recent_col1:
            st.write("**Recent Notes**")
            if notes:
                recent_notes = sorted(notes, key=lambda x: x.get("created_at", ""), reverse=True)[:5]
                for note in recent_notes:
                    note_date = note.get("created_at", "")[:10] if note.get("created_at") else "Unknown"
                    st.write(f"• {note.get('title', 'Untitled')} - {note_date}")
            else:
                st.info("No notes yet")
        
        with recent_col2:
            st.write("**Recent Tasks**")
            if tasks:
                recent_tasks = sorted(tasks, key=lambda x: x.get("created_at", ""), reverse=True)[:5]
                for task in recent_tasks:
                    status_icon = "✅" if task.get("status") == "completed" else "🔄"
                    task_desc = task.get("description", "No description")[:50]
                    st.write(f"{status_icon} {task_desc}...")
            else:
                st.info("No tasks yet")
        
        # Task Completion Timeline
        if tasks:
            st.divider()
            st.subheader("📊 Task Completion Timeline")
            task_df = pd.DataFrame(tasks)
            completed_tasks_df = task_df[task_df["status"] == "completed"].copy()
            
            if not completed_tasks_df.empty and "completed_at" in completed_tasks_df.columns:
                completed_tasks_df["completed_at"] = pd.to_datetime(completed_tasks_df["completed_at"], errors='coerce')
                completed_tasks_df = completed_tasks_df.dropna(subset=["completed_at"])
                if not completed_tasks_df.empty:
                    completed_tasks_df["date"] = completed_tasks_df["completed_at"].dt.date
                    completion_timeline = completed_tasks_df.groupby("date").size()
                    st.line_chart(completion_timeline)
                else:
                    st.info("No completed tasks with dates yet")
            else:
                st.info("Complete some tasks to see the completion timeline!")

    elif page == "Diary":
        st.header("Your Notes")
        notes = load_notes(access_token)
        
        if not notes:
            st.info("No notes yet. Create your first note below!")
        else:
            for idx, note in enumerate(notes):
                note_id = note.get("id")
                note_title = note.get("title") or "Untitled"
                note_date = note.get("created_at", "")
                
                with st.expander(f"📝 {note_title} - {note_date[:10] if note_date else ''}"):
                    # Display note content with markdown support
                    st.markdown(note.get("content", ""))
                    
                    # Display tags
                    note_tags = note.get("tags", [])
                    if note_tags:
                        st.write("**Tags:**", ", ".join(note_tags))
                    
                    # Edit and Delete buttons
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        if st.button("✏️ Edit", key=f"edit_{note_id}"):
                            st.session_state[f"editing_note_{note_id}"] = True
                            st.rerun()
                    
                    with col2:
                        if st.button("🗑️ Delete", key=f"delete_{note_id}"):
                            st.session_state[f"delete_confirm_{note_id}"] = True
                            st.rerun()
                    
                    # Edit form (shown when edit button is clicked)
                    if st.session_state.get(f"editing_note_{note_id}", False):
                        st.divider()
                        st.subheader("Edit Note")
                        
                        edit_title = st.text_input("Title", value=note.get("title", ""), key=f"edit_title_{note_id}")
                        edit_content = st.text_area("Content", value=note.get("content", ""), height=200, key=f"edit_content_{note_id}")
                        edit_tags_str = st.text_input("Tags (comma separated)", value=", ".join(note_tags), key=f"edit_tags_{note_id}")
                        
                        col_save, col_cancel = st.columns([1, 1])
                        with col_save:
                            if st.button("💾 Save Changes", key=f"save_{note_id}"):
                                edit_tags = [t.strip() for t in edit_tags_str.split(",")] if edit_tags_str else []
                                update_note(access_token, note_id, edit_title, edit_content, edit_tags)
                                st.session_state[f"editing_note_{note_id}"] = False
                        
                        with col_cancel:
                            if st.button("❌ Cancel", key=f"cancel_{note_id}"):
                                st.session_state[f"editing_note_{note_id}"] = False
                                st.rerun()
                    
                    # Delete confirmation
                    if st.session_state.get(f"delete_confirm_{note_id}", False):
                        st.warning(f"⚠️ Are you sure you want to delete '{note_title}'? This action cannot be undone.")
                        col_yes, col_no = st.columns([1, 1])
                        with col_yes:
                            if st.button("✅ Yes, Delete", key=f"confirm_delete_{note_id}", type="primary"):
                                delete_note(access_token, note_id)
                                st.session_state[f"delete_confirm_{note_id}"] = False
                        with col_no:
                            if st.button("❌ Cancel", key=f"cancel_delete_{note_id}"):
                                st.session_state[f"delete_confirm_{note_id}"] = False
                                st.rerun()

        st.divider()
        st.subheader("Create a New Note")
        title = st.text_input("Title")
        content = st.text_area("Content")
        tags_str = st.text_input("Tags (comma separated)")
        if st.button("Create Note"):
            tags = [t.strip() for t in tags_str.split(",")] if tags_str else []
            # For simplicity, use backend to determine user ID via token; we call /notes with user_id dummy (ignored if user not admin)
            # We need user_id: we will fetch from token's 'sub' claim; decode token via our backend not accessible here.
            # As a workaround, we call an endpoint to get current user info? none provided; thus we ask user to input their own ID.
            # For this demo, we assume user ID equals username (note: backend uses UUID). This may fail; but sample seed uses default.
            # Decode JWT to extract user ID (sub claim) without verification
            import base64
            try:
                # JWT is three parts: header.payload.signature
                parts = access_token.split(".")
                payload_json = base64.urlsafe_b64decode(parts[1] + "==").decode()
                payload = json.loads(payload_json)
                user_id = payload.get("sub")
            except Exception:
                user_id = None
            if not user_id:
                st.error("Unable to determine user ID from token. Please log in again.")
            else:
                create_note(access_token, tenant_id, user_id, title, content, tags)
            st.experimental_rerun()

    elif page == "Search":
        st.header("🔍 Advanced Search")
        
        # Main search query
        query = st.text_input("Enter your question or keywords", placeholder="e.g., 'What did I write about meetings?'")
        
        # Advanced filters
        with st.expander("🔧 Advanced Filters", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("From Date", value=None, help="Filter notes from this date")
                tags_input = st.text_input("Tags (comma-separated)", placeholder="e.g., work, personal", help="Filter by tags")
            with col2:
                end_date = st.date_input("To Date", value=None, help="Filter notes until this date")
                keyword_search = st.checkbox("Also use keyword search", help="Combine semantic and keyword search for better results")
        
        top_k = st.slider("Number of results", 1, 20, 5)
        
        if st.button("🔍 Search", type="primary") and query:
            with st.spinner("Searching your notes..."):
                result = search_notes(
                    access_token, 
                    query, 
                    top_k,
                    start_date=start_date.isoformat() if start_date else None,
                    end_date=end_date.isoformat() if end_date else None,
                    tags=tags_input if tags_input else None,
                    keyword_search=keyword_search,
                )
            
            if result:
                answer = result.get("answer", "")
                chunks = result.get("chunks", [])
                tasks = result.get("tasks", [])
                
                if answer and answer != "No relevant notes found.":
                    st.subheader("💡 Answer")
                    st.info(answer)
                
                if chunks:
                    st.subheader(f"📄 Top Results ({len(chunks)} found)")
                    for idx, item in enumerate(chunks, 1):
                        with st.expander(f"Result {idx} (Relevance: {item.get('score', 0):.2%})"):
                            st.write(item.get('text', ''))
                elif not answer or answer == "No relevant notes found.":
                    st.info("No relevant notes found. Try different keywords or create more notes!")
                
                if tasks:
                    st.subheader("✅ Extracted Tasks")
                    for task in tasks:
                        due_date = f" (due {task['due_date']})" if task.get('due_date') else ""
                        st.write(f"• {task['description']}{due_date}")
            else:
                st.warning("No results found. Try a different search query.")

    elif page == "Tasks":
        st.header("✅ Tasks")
        status_filter = st.selectbox("Filter by status", ["all", "open", "completed"], key="task_filter")
        
        with st.spinner("Loading tasks..."):
            tasks_list = load_tasks(access_token, None if status_filter == "all" else status_filter)
        
        if not tasks_list:
            st.info(f"No {status_filter if status_filter != 'all' else ''} tasks found. Tasks are automatically extracted when you search your notes!")
        else:
            st.write(f"**Found {len(tasks_list)} task(s)**")
            for task in tasks_list:
                task_id = str(task.get("id", ""))
                task_desc = task.get("description", "No description")
                task_status = task.get("status", "open")
                due_date = task.get("due_date")
                
                with st.container():
                    cols = st.columns([4, 1, 1])
                    with cols[0]:
                        status_icon = "✅" if task_status == "completed" else "🔄"
                        st.write(f"{status_icon} **{task_desc}**")
                        if due_date:
                            st.caption(f"Due: {due_date}")
                    with cols[1]:
                        status_badge = "✅ Completed" if task_status == "completed" else "🔄 Open"
                        st.write(status_badge)
                    with cols[2]:
                        if task_status != "completed":
                            if st.button("✓ Complete", key=f"complete_{task_id}", type="primary"):
                                complete_task(access_token, task_id)
                st.divider()


if __name__ == "__main__":
    main()