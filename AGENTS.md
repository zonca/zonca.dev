# Agent notes

- Review GEMINI.md before working—contains project-specific guidance and expectations.

## Buffer Social Media

### Setup
- Buffer skill located at: `/home/zonca/.agents/skills/buffer/SKILL.md`
- Uses GraphQL API at `https://api.buffer.com`
- Environment variable `BUFFER_KEY` must be set

### Channel IDs (organization: 655270181efd918df3d33eff)
| Platform | Channel ID |
|----------|------------|
| Twitter/X | `6552702d7a6cf4d23f916d5c` |
| LinkedIn | `67c6746b3b85969eafee1ee4` |
| Bluesky | `67c6738e3b85969eafe22a07` |

### Quick post creation
```bash
buffer_query() {
  curl -s -X POST "https://api.buffer.com" \
    -H "Authorization: Bearer $BUFFER_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"$1\"}"
}

buffer_query "mutation { createPost(input: { text: \"POST TEXT\", channelId: \"CHANNEL_ID\", schedulingType: automatic, mode: addToQueue }) { ... on PostActionSuccess { post { id text dueAt } } ... on MutationError { message } } }"
```

### Workflow for new blog posts
1. Read the post content
2. Draft 1 announcement post adapted for each platform (Twitter: short + hashtags, LinkedIn: professional with bullet points, Mastodon/Bluesky: similar to Twitter)
3. Show drafts to user for approval
4. Once approved, queue to all 3 channels using Buffer API
