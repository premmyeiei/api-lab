# API lab results

## Part 0
- Step 0.1, the number of pizza names: 18
- Step 0.3, status code of the request without a token: 401
- Step 0.4, the name of your pizza: An Empty Frutti di Mare
- Step 0.12, results of the three runs without a session (optional): Run 1: FAILED (401 Unauthorized), Run 2: FAILED (401 Unauthorized), Run 3: FAILED (401 Unauthorized)
- Step 0.16, blocks of "how many of the three tools are excluded": 0 tools excluded (`[]`), 1 tool excluded (e.g. `["Knife"]`), 2 tools excluded (e.g. `["Knife", "Scissors"]`), all 3 tools excluded (`["Knife", "Pizza cutter", "Scissors"]`)

## Defect report
- Title: Excluding all three cutting tools in `POST /api/pizza` returns 500 Internal Server Error with an empty body instead of 400 Bad Request
- Request: `POST https://quickpizza.grafana.com/api/pizza` with header `Authorization: token abcdef0123456789` and JSON body `{"excludedTools": ["Knife", "Pizza cutter", "Scissors"]}`
- Expected result: Status `400 Bad Request` with a JSON error message explaining that no pizza can satisfy the request when all cutting tools are excluded.
- Actual result: Status `500 Internal Server Error` with an empty body (`Content-Length: 0`).
- Severity: High (Medium/High) — A valid client request with unsatisfiable filter constraints triggers an unhandled server error (`500`) and returns an empty non-JSON body, breaking API contract expectations and potentially crashing client JSON parsers.

## Part A
- Step A4, status codes when the other user reads, changes and deletes: Read (`GET`): `404`, Change (`PUT`): `400`, Delete (`DELETE`): `400`

## Part B
1. **Failures found by API tests vs. unit tests with stubs:**
   - **Two kinds of failure API tests can find that unit tests with stubs cannot:**
     1. **Infrastructure and multi-server state/routing failures:** For example, load-balancer session affinity (`AWSALB` cookies) failing to route subsequent requests to the backend instance that holds the newly created user or rating, or real database/storage integration errors.
     2. **HTTP contract, serialization, and middleware failures:** Issues with real JSON marshaling/unmarshaling, authentication header parsing, HTTP status codes, and unhandled server crashes (`500 Internal Server Error` with an empty body).
   - **One reason to write unit tests with stubs as well:** Unit tests with stubs execute in milliseconds without network latency or external server dependencies, making them completely deterministic and able to isolate the exact function or branch of business logic where a bug occurred.
2. **Why every test creates its own user rather than using the public token, and how this applies to Project 2:**
   - QuickPizza is shared simultaneously by everyone practising on it. Ratings created with the public token (`abcdef0123456789`) belong to the shared public account, so concurrent runs by other students could modify or delete those ratings mid-test (causing flaky failures), or our tests could corrupt shared data. Creating a fresh user (`lab-<uuid>`) per test isolates each test's data so every test is independent.
   - In **Project 2** (on the shared shop or hotel), we will use fixtures to create fresh, uniquely identified test resources (e.g., a new cart, customer, or booking) before each test and clean them up (`DELETE`) after the test completes, never modifying or deleting shared baseline data or data created by other groups.
3. **Why the tests send every request through one session, and what happened in Step 0.12:**
   - QuickPizza runs across multiple server instances behind a load balancer, and each instance keeps its own users and ratings in memory. The load balancer sends back an `AWSALB` cookie on the first response to pin subsequent requests to that same server. Sending every request through one `requests.Session` preserves the `AWSALB` cookie automatically so every request in the test run reaches the same backend server.
   - In **Step 0.12**, when we ran `test_no_session.py` three times without a session (`requests.post` on its own), **all three runs failed with `401 Unauthorized`** on the login step because the login request had no cookie and was routed by the load balancer to a server instance that had never seen the user created in the previous request.
4. **Excluded tools defect in Step 0.16:**
   - **Which block revealed the defect:** The block where **all 3 tools are excluded** (`["Knife", "Pizza cutter", "Scissors"]`).
   - **Why a 500 with an empty body is worse than a 400 with a message:** Status `500` tells the calling application that the server crashed unexpectedly (which may cause clients or gateways to retry the request assuming a transient outage) rather than indicating invalid user input (`400`). Furthermore, an empty body causes `res.json()` in client apps to fail with a JSON decode error and gives the user no explanation of how to fix their request.
   - **Why the test stays in the suite as `xfail` instead of being deleted:** Marking the test with `@pytest.mark.xfail(..., strict=True)` documents the known bug and keeps it visible in test reports while keeping the overall test suite green. With `strict=True`, if QuickPizza fixes the bug in the future, the test will unexpectedly pass and fail the test run (`XPASS(strict)`), reminding us to remove the `xfail` mark and keep the passing test as a permanent regression check.
5. **Base choice coverage vs. all combinations coverage in Step A1:**
   - The input domain model in Step A1 has 4 characteristics with $3, 4, 2,$ and $3$ blocks respectively:
     - $C_1$ (Value of stars): $3$ blocks
     - $C_2$ (Type of stars): $4$ blocks
     - $C_3$ (Pizza): $2$ blocks
     - $C_4$ (Token): $3$ blocks
   - **Base choice coverage needs 9 tests:** $1$ base test (all base blocks) plus $(b_i - 1)$ tests for each characteristic changing one block at a time while keeping the others at their base:
     $$1 + (3 - 1) + (4 - 1) + (2 - 1) + (3 - 1) = 1 + 2 + 3 + 1 + 2 = 9\text{ tests}$$
   - **All combinations coverage would need 72 tests:** multiplying the number of blocks in every characteristic:
     $$3 \times 4 \times 2 \times 3 = 72\text{ tests}$$
6. **Status codes in Step A4 when the other user reads, changes, and deletes a rating:**
   - **Actual codes returned:** `404 Not Found` when reading (`GET`), `400 Bad Request` when changing (`PUT`, with body `{"error": "rating ID ... not found"}`), and `400 Bad Request` when deleting (`DELETE`, with body `{"error": "rating ID ... not found"}`).
   - **Expected codes:** Either `403 Forbidden` (since the caller is authenticated with a valid token but does not own the resource) or consistently `404 Not Found` across all three operations (to avoid leaking whether the rating ID exists for another user).
   - **Is the difference a defect?** Access control itself works (all three attempts are refused and the rating is unchanged), but returning `400 Bad Request` for `PUT` and `DELETE` while returning `"rating ID ... not found"` in the message is a minor status-code defect/inconsistency. A well-formed request targeting a resource that does not exist for that user should return `404 Not Found` (consistent with `GET`) or `403 Forbidden`, not `400 Bad Request`.
7. **Made-up 16-character token (`Authorization: token 0000000000000000`):**
   - **What comes back:** `200 OK` with a JSON body containing the list of ratings from the shared/default account (`{"ratings": [{"id": 1, "stars": 5, "pizza_id": 1}, ...]}`).
   - **Is this a defect, and what could a stranger do with it on a real system?** Yes, this is a **severe authentication defect**. QuickPizza checks only that the token is 16 characters long rather than verifying that the token was actually generated by logging in, falling back to the default user for any unknown 16-character token. On a real system, an unauthenticated attacker could invent any 16-character token to bypass authentication completely and read, create, modify, or delete data without valid credentials.
8. **API tests vs. web page (UI) tests:**
   - **One thing an API test checks better than a test through the web pages:** API tests directly verify HTTP status codes, response headers, exact JSON bodies, and backend rejection of invalid or malicious inputs (such as out-of-range values, wrong data types, missing fields, or unauthorized requests across users) that the web UI might block on the client side, and they run orders of magnitude faster and less flakily than browser tests.
   - **One thing that only a test through the web pages can check:** Only a test through the web pages can verify the visual presentation and user interface behavior in a browser—such as whether buttons, forms, and error messages actually render on the screen, whether CSS layout is usable, and whether client-side JavaScript interactions work for a human user.

