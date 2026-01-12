# API Standards (The "What")
Universal principles for designing and implementing APIs in enterprise applications.

## 1. Design Principles

- **RESTful Architecture**: Follow REST principles (stateless, resource-based, uniform interface).
- **Versioning**: Use URL-based versioning (e.g., `/v1/resource`) for breaking changes. Support multiple versions simultaneously.
- **Resource Naming**: Use plural nouns, lowercase, hyphens for multi-word (e.g., `/users`, `/user-profiles`).
- **HTTP Methods**: Standard CRUD operations (GET, POST, PUT, DELETE, PATCH).

## 2. Security

- **Authentication**: Use OAuth 2.0 or JWT. Never basic auth in production.
- **Authorization**: Implement role-based access control (RBAC).
- **Rate Limiting**: Enforce per-user/IP limits to prevent abuse.
- **Input Validation**: Validate all inputs; sanitize for injection attacks.
- **HTTPS Only**: All APIs must use TLS 1.3+.

## 3. Data Handling

- **Pagination**: Use cursor-based pagination for large datasets.
- **Filtering/Sorting**: Support query parameters (e.g., `?filter=status:active&sort=name`).
- **Response Formats**: JSON as default; support content negotiation.
- **Error Responses**: Use standard HTTP status codes; include error details in response body.

## 4. Documentation

- **OpenAPI/Swagger**: All endpoints must be documented with OpenAPI 3.0+.
- **Examples**: Provide request/response examples.
- **Deprecation**: Clearly mark deprecated endpoints with sunset headers.

## 5. Performance & Reliability

- **Caching**: Implement appropriate caching (ETags, Cache-Control).
- **Monitoring**: Log requests/responses; use APM tools.
- **Backwards Compatibility**: Avoid breaking changes; use feature flags for gradual rollouts.

## 6. Compliance

- **Data Privacy**: Adhere to GDPR/CCPA for PII handling.
- **Audit Logging**: Log all access for compliance audits.
