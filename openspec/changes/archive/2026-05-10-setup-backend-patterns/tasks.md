# Tasks: setup-backend-patterns

## 1. BaseRepository[T] Implementation

- [x] 1.1 Create `app/core/repositories/__init__.py`
- [x] 1.2 Create `app/core/repositories/base.py` with generic BaseRepository[T] class
- [x] 1.3 Implement create() method
- [x] 1.4 Implement get() method
- [x] 1.5 Implement get_all() method
- [x] 1.6 Implement update() method
- [x] 1.7 Implement delete() method
- [x] 1.8 Add base tests for BaseRepository

## 2. Unit of Work Implementation

- [x] 2.1 Create `app/core/uow.py` with UnitOfWork class
- [x] 2.2 Implement context manager (\_\_enter\_\_, \_\_exit\_\_)
- [x] 2.3 Implement commit on successful exit
- [x] 2.4 Implement rollback on exception
- [x] 2.5 Implement register() method for repositories
- [x] 2.6 Add base tests for UnitOfWork

## 3. Dependency Injection Patterns

- [x] 3.1 Create `app/core/dependencies.py`
- [x] 3.2 Implement get_db() dependency using existing session from setup-backend-config
- [x] 3.3 Create repository factory function
- [x] 3.4 Implement get_usuario_repo() as FastAPI Depends
- [x] 3.5 Implement get_uow() as FastAPI Depends
- [x] 3.6 Add integration tests for dependencies

## 4. Verification

- [x] 4.1 Run pytest to verify all tests pass
- [x] 4.2 Verify imports work correctly
- [x] 4.3 Test that get_db provides valid session