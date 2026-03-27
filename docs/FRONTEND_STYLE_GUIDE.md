# Frontend Style Guide

Last reviewed: 2026-03-27

## Purpose

This document defines the minimum frontend styling contract for CfHEE.

It is intentionally small.

## Mandatory theme baseline

- CfHEE frontend uses a dark theme by default.
- New frontend components must stay within that dark theme.
- Light card or panel backgrounds are not allowed.

## Card baseline

Cards and panels should use the shared dark-surface baseline:

- elevated dark background
- visible dark-theme border
- rounded corners
- consistent internal spacing
- consistent shadow depth

Current shared utility classes:

- `surface-panel`
- `surface-card`

These should be preferred over one-off local surface colors for new frontend components.

## Consistency rules

- New frontend components should reuse the shared surface utilities when rendering cards or panels.
- Do not introduce light backgrounds for cards, panels, or path/status tiles.
- If a new reusable surface shape is needed later, extend the shared styling contract instead of adding isolated per-page visual rules.

## Current practical scope

This guide does not introduce a full design system.

It only establishes:

- dark theme as mandatory
- a shared surface baseline
- a no-light-background rule for new work
