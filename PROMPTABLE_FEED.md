# Promptable Feed Algorithm

A personalized content curation feature that allows users to describe what they want to see in their social feed using natural language.

## Overview

The promptable feed algorithm lets users control their content experience by simply telling the system what they're interested in (or not interested in) using plain English. The system parses these preferences and applies intelligent filtering to the social feed.

## Features

### 🎯 Natural Language Preferences
Users can describe their preferences in conversational language:

```
"Show me science and technology posts, but no politics"
"I want to see posts about climate change with high trust scores"
"Show verified posts only, exclude sports and entertainment"
```

### 🔍 Smart Parsing
The system automatically extracts:
- **Topics to include** - Show posts about these subjects
- **Topics to exclude** - Hide posts about these subjects
- **Trust score requirements** - Minimum quality threshold
- **Verification requirements** - Show only verified content

### ⚡ Real-time Application
Preferences are applied instantly to your feed with no caching delay.

### 👁️ Preview Mode
Test your preferences before applying them to see exactly what filters will be created.

## API Endpoints

### Preview Preferences
**`POST /v1/feed-preferences/preview`**

Test how your prompt will be parsed without saving it.

```bash
curl -X POST "http://localhost:8000/v1/feed-preferences/preview" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Show me science and technology, but no politics"
  }'
```

**Response:**
```json
{
  "prompt": "Show me science and technology, but no politics",
  "parsed_filters": {
    "interests": ["science", "technology"],
    "exclude_topics": ["politics"],
    "keywords_include": [],
    "keywords_exclude": [],
    "min_trust_score": null,
    "require_verified": false
  },
  "explanation": "✅ Include posts about: science, technology\n❌ Exclude posts about: politics"
}
```

### Get Current Preferences
**`GET /v1/feed-preferences/me`**

Retrieve your current feed preferences.

```bash
curl "http://localhost:8000/v1/feed-preferences/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create/Update Preferences
**`POST /v1/feed-preferences/me`**

Set your feed preferences. This will create new preferences or update existing ones.

```bash
curl -X POST "http://localhost:8000/v1/feed-preferences/me" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "I want to see posts about AI and machine learning with high trust scores. No politics or sports."
  }'
```

### Update Specific Fields
**`PATCH /v1/feed-preferences/me`**

Update just the prompt or enable/disable filtering.

```bash
# Disable filtering temporarily
curl -X PATCH "http://localhost:8000/v1/feed-preferences/me" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"active": false}'
```

### Delete Preferences
**`DELETE /v1/feed-preferences/me`**

Remove your preferences and return to the default feed.

```bash
curl -X DELETE "http://localhost:8000/v1/feed-preferences/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Personalized Feed
**`GET /v1/social/feed/personalized`**

Get your personalized feed based on your preferences.

```bash
curl "http://localhost:8000/v1/social/feed/personalized?limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Usage Examples

### Example 1: Topic-Based Filtering

```json
{
  "prompt": "Show me science, technology, and climate posts. Exclude politics and entertainment."
}
```

**Result:**
- ✅ Posts about science, technology, climate
- ❌ Posts about politics, entertainment

### Example 2: Quality Filtering

```json
{
  "prompt": "Show me high trust score posts about research and data"
}
```

**Result:**
- ✅ Posts with trust_score >= 5
- ✅ Posts containing "research" or "data"

### Example 3: Verified Content Only

```json
{
  "prompt": "Show verified posts only, exclude rumors and unverified claims"
}
```

**Result:**
- ✅ Only posts with trust_score >= 10 (verified)
- ❌ Posts containing "rumor" or "unverified"

### Example 4: Complex Preferences

```json
{
  "prompt": "I want to see posts about artificial intelligence, machine learning, and neural networks with a trust score above 7. No politics, no sports, no entertainment."
}
```

**Result:**
- ✅ Posts about AI, ML, neural networks
- ✅ Only posts with trust_score >= 7
- ❌ Politics, sports, entertainment

## How It Works

### 1. Prompt Parsing

The system uses pattern matching to extract structured filters from natural language:

```python
# User writes:
"Show me science and technology, but no politics"

# System parses to:
{
  "interests": ["science", "technology"],
  "exclude_topics": ["politics"],
  "min_trust_score": null,
  "require_verified": false
}
```

### 2. Filter Application

Filters are applied to the SQL query:

- **Interests**: Search in post tags, title, and content
- **Exclusions**: Filter out matching posts
- **Trust Score**: Apply minimum threshold
- **Verification**: Require high trust scores

### 3. Ranking

Results are ranked by:
1. Trust score (descending)
2. Recency (descending)

This ensures high-quality, recent content appears first.

## Supported Patterns

### Include Topics
```
"Show me [topic]"
"I want to see posts about [topic]"
"Include [topic]"
"Topics: [topic1], [topic2]"
"Interests: [topic]"
```

### Exclude Topics
```
"But no [topic]"
"Exclude [topic]"
"Don't want [topic]"
"Avoid [topic]"
"Hide [topic]"
```

### Trust Score
```
"Trust score above [number]"
"Minimum trust score [number]"
"High trust"
"Good trust"
```

### Verification
```
"Verified posts only"
"Only verified"
"Show verified"
```

## Database Schema

### FeedPreference Model

```python
class FeedPreference(Base):
    id: int
    member_id: int  # Unique - one preference per user
    prompt: str  # Natural language prompt
    parsed_filters: dict  # Structured filter JSON
    last_applied_at: datetime  # Last time feed was fetched
    active: bool  # Enable/disable filtering
    created_at: datetime
    updated_at: datetime
```

## Frontend Integration

### React/TypeScript Example

```typescript
// Set preferences
async function setFeedPreferences(prompt: string) {
  const response = await fetch('/v1/feed-preferences/me', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ prompt })
  });
  return response.json();
}

// Get personalized feed
async function getPersonalizedFeed(limit = 20, offset = 0) {
  const response = await fetch(
    `/v1/social/feed/personalized?limit=${limit}&offset=${offset}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  return response.json();
}

// Preview before applying
async function previewPreferences(prompt: string) {
  const response = await fetch('/v1/feed-preferences/preview', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ prompt })
  });
  return response.json();
}
```

## Testing

### Run Migration

```bash
cd server
poetry run alembic upgrade head
```

### Test API

```bash
# 1. Login to get token
TOKEN=$(curl -X POST "http://localhost:8000/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email_or_username": "user@example.com", "password": "SecurePass123"}' \
  | jq -r '.access_token')

# 2. Preview preferences
curl -X POST "http://localhost:8000/v1/feed-preferences/preview" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show me science posts, no politics"}' | jq

# 3. Set preferences
curl -X POST "http://localhost:8000/v1/feed-preferences/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show me science posts, no politics"}' | jq

# 4. Get personalized feed
curl "http://localhost:8000/v1/social/feed/personalized?limit=10" \
  -H "Authorization: Bearer $TOKEN" | jq
```

## Future Enhancements

### Short Term
- [ ] More sophisticated NLP parsing (spaCy, NLTK)
- [ ] Author preferences (follow/block specific users)
- [ ] Time-based preferences (recent content only)
- [ ] Language filtering

### Medium Term
- [ ] Machine learning-based recommendations
- [ ] Collaborative filtering (similar users)
- [ ] Topic clustering and discovery
- [ ] Sentiment filtering

### Long Term
- [ ] Multi-language support
- [ ] Visual preference builder UI
- [ ] A/B testing framework
- [ ] Preference analytics dashboard

## Performance Considerations

### Current Implementation
- Filters are applied at query time (no caching)
- Uses SQLAlchemy ORM with indexes
- Suitable for moderate traffic (< 10k users)

### Scaling Recommendations
- **Cache parsed filters** in Redis
- **Pre-compute feed** for heavy users
- **Use full-text search** (PostgreSQL tsvector or Elasticsearch)
- **Implement pagination cursors** for large result sets
- **Add query timeout** for complex filters

## Privacy & Security

- ✅ Preferences are private (per-user)
- ✅ Requires authentication to access
- ✅ No sharing of preference data between users
- ✅ Preferences can be deleted at any time
- ✅ No tracking of preference changes (audit log TBD)

## Troubleshooting

### Preferences not applying
1. Check that `active` is `true`
2. Verify filters were parsed correctly (use `/preview`)
3. Ensure matching posts exist in database

### Parse not working as expected
- The parser looks for specific patterns
- Try more explicit language
- Use preview endpoint to test
- Check supported patterns above

### Performance issues
- Reduce complexity of filters
- Add more specific topics (fewer broad terms)
- Consider pagination with smaller limits

## Related Documentation

- **API Docs**: http://localhost:8000/docs
- **Security Features**: `../SECURITY_FIXES.md`
- **Database Schema**: `../docs/architecture.md`
