# BOOK INVENTORY BACKEND
REST API for managing books and their inventory

## Index

- [Project status](#project-status)
- [Goal](#goal)
- [Scope](#scope)
    - [Includes](#includes)
    - [Does not include (for now)](#does-not-include-for-now)
- [Design](#design)
    - [Domain model (high level)](#domain-model-high-level)
- [Business rules](#business-rules)
- [How to execute](#how-to-execute)
- [What would improve next time?](#what-would-improve-next-time)

🚧 **Project status**

Currently in initial design phase.

First objective:

Clearly define the domain and rules before writing code.


## 🎯Goal

Provide a solid foundation for managing:

- Bookkeeping

- Book-based stock control

- Inventory movements (incoming and outgoing)

- Strict validation of business rules

- The project is designed to grow incrementally following well-defined sprints.

## Scope


### Includes

- REST API built with FastAPI

- Relational database persistence

- Explicit domain model:

    - Book

    - Inventory

    - InventoryMovement

- Business rules for stock management

- Inventory movement history

- Tests for critical rules

### Does not include (for now)

- Authentication/authorisation

- User or role management

- External integrations

- Graphical interface (frontend)

## Design

### 🧱 Domain model (high level)

**Book**: basic information about the book

**Inventory**: current stock per book

**InventoryMovement**: historical record of stock changes (IN/OUT)

Each movement impacts the inventory and is recorded for auditing purposes.

## Business rules

- Stock can never be negative.

- Any change in stock must generate a movement.

- Stock removals are rejected if there is insufficient quantity.

## How to execute

## What would improve next time?

