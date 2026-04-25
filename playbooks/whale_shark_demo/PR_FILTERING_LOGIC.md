# PR Filtering Logic - Simple Outline

This document describes the optimized task flow for finding and filtering PRs that need whale shark comments.

## Task Flow

### 1. find_prs.yml
- Search GitHub: `created:<=7 days AND updated:<=1 day`
  - Pre-filter: old PRs without very recent activity
  - Excludes PRs with any updates (commits, comments, labels, etc.) in last 24h
- Output: `pr_list` (all old PRs without updates in 24h)

### 2. get_pr_details.yml
- For each PR in pr_list:
  - Get PR details (`method: get`) → `pushed_at`, `created_at`, `mergeable_state`, etc.
- Output: `pr_details_map`

### 3. get_pr_comments.yml
- For each PR in pr_list:
  - Get PR comments (`method: get_comments`)
- Output: `pr_comments`

### 4. filter_prs.yml (COMBINED filtering)
- For each PR in pr_list:
  
  **a. Calculate real activity:**
  - `last_non_whale_comment` = latest comment where body !~ whale_shark pattern
  - `last_real_activity` = max(`pushed_at`, `last_non_whale_comment`)
  
  **b. Check whale shark recency:**
  - `last_whale_comment` = latest comment where body ~ whale_shark pattern
  
  **c. Include PR if BOTH conditions met:**
  - `last_real_activity >= days_last_activity_threshold` (e.g., 3 days)
  - `(no last_whale_comment OR last_whale_comment >= comment_freshness_days)` (e.g., 7 days)

- Output: `prs_to_comment`, `pr_activity_map`

### 5. Get zen/status
- Fetch once, not per-PR
- Only if `prs_to_comment` is not empty

### 6. Post comments
- Post whale shark comments on `prs_to_comment`

## Benefits

**Pre-filtering with `updated:<=1 day`:**
- Avoids API calls for PRs with commits/reviews in last 24h (obviously active)
- Still catches PRs where we commented 2+ days ago (won't miss them)
- Reduces N in the 2N API calls (details + comments)

**Combined filtering:**
- Single loop through PR data instead of two separate filters
- Checks both real activity and whale shark comment recency together
- More efficient and easier to maintain

## Variables

- `days_created_threshold`: How old PR must be (default: 7 days)
- `days_last_activity_threshold`: How long since real activity (default: 3 days)
- `comment_freshness_days`: How long since last whale shark comment before re-commenting (default: 7 days)

## Real Activity Definition

Real activity = latest of:
- Commits pushed (`pushed_at` from PR details)
- Non-whale-shark comments (human reviews, questions, etc.)

Whale shark comments do NOT count as real activity.
