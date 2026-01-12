# Code Review Template
Use this template when conducting a code review for [LANGUAGE] code.

## Context
- **Project**: [PROJECT_NAME]
- **Language**: [LANGUAGE]
- **Framework**: [FRAMEWORK]
- **Files Changed**: [LIST_OF_FILES]
- **PR Description**: [BRIEF_DESCRIPTION]

## Review Checklist

### 1. Architecture & Design
- [ ] Follows the Five-View Architecture framework
- [ ] Adheres to [LANGUAGE] coding standards
- [ ] Proper separation of concerns
- [ ] No violations of forbidden patterns

### 2. Security
- [ ] Input validation implemented
- [ ] No hardcoded secrets
- [ ] Proper authentication/authorization
- [ ] SQL injection/XSS prevention

### 3. Code Quality
- [ ] Type safety (if applicable)
- [ ] Meaningful variable/function names
- [ ] DRY principle followed
- [ ] Code is readable and maintainable

### 4. Testing
- [ ] Unit tests added/updated
- [ ] Integration tests if needed
- [ ] Edge cases covered
- [ ] Test coverage maintained

### 5. Performance
- [ ] No obvious performance issues
- [ ] Efficient algorithms used
- [ ] Database queries optimized

### 6. Documentation
- [ ] Code comments where needed
- [ ] Public APIs documented
- [ ] README updated if necessary

## Specific Feedback
[DETAILED_COMMENTS_HERE]

## Approval Status
- [ ] Approved
- [ ] Approved with minor changes
- [ ] Requires major revisions
- [ ] Rejected

## Next Steps
[RECOMMENDATIONS_FOR_IMPROVEMENT]