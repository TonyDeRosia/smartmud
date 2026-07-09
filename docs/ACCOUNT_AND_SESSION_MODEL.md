# Account and Session Model

Smart MUD Phase 2D replaces the temporary auto-loaded `Player` flow with local accounts, runtime sessions, account-owned characters, and a permission foundation.

## Accounts

Accounts are stored in SQLite in `accounts` with `account_id`, `username`, auth placeholders (`password_hash` or `local_dev_auth_token`), timestamps, status, role, optional email, and notes. Phase 2D uses local development auth tokens/placeholders only; plaintext passwords are not stored.

Roles are `player`, `builder`, `immortal`, and `admin`.

## Sessions

Runtime sessions track `session_id`, `transport_type`, `account_id`, `character_id`, `world_id`, `remote_address`, connection/activity timestamps, authentication status, and state.

Session states are `connected`, `account_login`, `account_create`, `character_select`, `character_create`, `playing`, and `disconnected`.

## Character ownership

Characters are account-owned. Character selection and world entry filter by account, and entering another account's character is rejected. Legacy orphan characters are attached to the first local development account when an account is created, preserving developer convenience.

## Permissions

Permission helpers map account/character role fields and builder flags to `is_player`, `is_builder`, `is_immortal`, `is_admin`, `can_build`, `can_use_wizhelp`, `can_edit_world_package`, and `can_manage_accounts`. These helpers provide a foundation only; no Builder Mode/admin commands are added in this phase.

## Web flow

The web API exposes account/session endpoints, character listing/creation/entry endpoints, and keeps existing MUD play/input routes. The UI starts at an Account screen, proceeds to World and Character Select, then enters play.

## Telnet flow

Telnet now asks for an account name, offers local account creation, asks for a character name, creates/selects that character, enters the world, and routes commands normally.

## EventBus events

Account/session/character lifecycle events are published: `account_created`, `account_login`, `account_logout`, `session_created`, `session_authenticated`, `session_disconnected`, `character_created`, `character_selected`, `character_entered_world`, `character_left_world`, and `permission_checked` where applicable.
