# Domain Model

## Hierarchy
Workspace
  -> Domain
    -> Project
      -> Client
        -> Module

## Minimum required on document ingest
- workspace
- domain
- source_type
- title
- raw_text

## Optional
- project
- client
- module
- language
- source_ref

## Rule
User-provided top-level scope is authoritative.
Model-generated tags are advisory only.