# 🎛 Board App Context

_Last updated: October 2025_  
**Maintainer:** Django Copilot 🔨🤖🔧  

---

## 🧩 Purpose

The **`board` app** powers FrancoUke’s interactive dashboard — a visual, Kanban-style interface that organizes **events, rehearsals, and messages** into columns such as **Upcoming**, **Past**, and **To Be Confirmed**.

Each `BoardColumn` contains data objects (`events`, `songs`, or `messages`) that are rendered via reusable **partials**.  
This modular design enables rich, dynamic updates and a streamlined performer workflow.

---

## ⚙️ Core Models & Relationships

| Model | Role | Key Relationships |
|--------|------|-------------------|
| `BoardColumn` | Represents a single board column (e.g. Upcoming, Past, Songs to Listen) | Has many `events`, `items`, `messages` |
| `Event`       | Represents a gig, show, or rehearsal                                    | Linked to `Venue`; may have a related `Setlist` |
| `EventAvailability` | Tracks performer attendance/availability per event | Links `User` ↔ `Event` |
| `BoardItem` | General items (songs, rehearsals, etc.) | Belongs to a `BoardColumn` |
| `Venue` | Location of an event | Has many `events` |

---

## 🧭 View Layer Overview

| View  | Purpose   | Temp. | Context |
|-------|-----------|-------|----------|
| `full_board_view()` 
        | Renders the **main board** with columns and event cards 
                    | `board/full_board.html` 
                            | `columns` (each with `sorted_events`, `sorted_messages`, etc.) |
| `event_detail()` | Returns an **event modal body** for AJAX detail requests | `partials/_event_detail.html` | `event`, `user_status`, `setlist` |
| `performer_event_list()` | Lists all upcoming events for logged-in performers | `board/performer_event_list.html` | `events`, `user_availability` |
| `availability_matrix()` | Shows all performers’ attendance in a matrix format | `board/availability_matrix.html` | `events`, `matrix`, `summary` |
| `rehearsal_detail_view()` | Displays rehearsal details | `board/rehearsal_detail.html` | `rehearsal`, `user_availability` |

---

## 🧩 Template & Partial Roles

| Partial | Description | Typically Rendered By |
|----------|--------------|------------------------|
| **`_event_card.html`** | Compact event summary on the board | Loop inside `full_board.html` |
| **`_event_detail.html`** | Modal body with full event description, time, and availability | `event_detail()` (AJAX) |
| **`_rehearsal_detail.html`** | Rehearsal-specific modal | `rehearsal_detail_view()` |
| **`item_gallery.html`** | Displays photos linked to a board item | `board_item_gallery_view()` |
| **`availability_matrix.html`** | Grid showing all users’ availability across events | `availability_matrix()` |

---

## 🎵 Setlist Integration Context

### Current State
- Setlists are only accessible directly via URL:  
  `http://127.0.0.1:8000/setlists/<id>/`
- They are not currently exposed on the main board interface.

### Enhancement Plan
- Add “🎵 View Setlist” or “➕ Create Setlist” buttons directly in **`_event_card.html`**.  
- Optionally show the same link in `_event_detail.html` (modal).
- Prefetch optimization:

  ```python
  .prefetch_related("events__setlist")
