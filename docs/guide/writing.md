# Write a test

## The shape of a test

Each test is one scenario. Its name and docstring say it in Given / When / Then form, and its body marks each part:

```python
def test_given_invoice_body_when_user_searches_invoice_then_that_request_shows(
    bin_page: BinPage, api: StudioApi
) -> None:
    """Given a request whose body holds "invoice", when the user searches "INVOICE", then only that request shows."""
    # Given
    api.send(bin_page.bin_id, path="/order", body=b'{"kind": "order"}')
    api.send(bin_page.bin_id, path="/bill", body=b'{"kind": "invoice"}')
    expect(bin_page.rows).to_have_count(2)
    # When
    bin_page.search("INVOICE")
    # Then
    expect(bin_page.rows).to_have_count(1)
    expect(bin_page.rows).to_contain_text("/bill")
```

## Rules

- **Tests hold no locators.** They talk to page objects in `src/webhook_studio_e2e/pages/`: `HomePage`, `BinPage`,
  `ConfirmDialog` and `ReplyDialog`. Both pages extend `AppPage`, which finds any text the page shows with
  `text(...)`. When a test needs a new part of a page, add it to the page object.
- **Locators go by role and label first** (`get_by_role`, `get_by_label`, `get_by_placeholder`), then by the app's
  `data-testid` attributes. Never by CSS classes or XPath, which change when the app's styling changes.
- **Only web-first assertions.** `expect(locator)` waits by itself; there are no sleeps.
- **Data comes through the REST API.** The `api` fixture makes bins and sends requests in milliseconds, so the
  browser does only what the scenario tests.
- **Each test makes its own bin** in its own browser context, so tests run in any order.
- **Wait for the app, not for time.** The app sets checkboxes and switches from its server, so page objects click
  them and wait for `to_be_checked()` rather than call `check()`.

## Fixtures

| Fixture     | Gives                                                                   |
| ----------- | ----------------------------------------------------------------------- |
| `settings`  | Where the apps are, from the `E2E_*` variables.                         |
| `api`       | A REST client for the `restricted` app.                                 |
| `local_api` | A REST client for the `local` app; the test skips when there is none.  |
| `home`      | The home page object, not yet opened.                                   |
| `bin_page`  | A new bin, opened and live.                                             |

## Browsers

Every test runs in Chromium, Firefox and WebKit. A test that only one browser can run carries
`@pytest.mark.only_browser("chromium")`, as the clipboard tests do: only Chromium lets a page read the clipboard.

## Accessibility and screenshots

- `assert_accessible(page)` in `tests/e2e/test_accessibility.py` scans what the page shows, once its animations end,
  and fails with each finding and the elements behind it.
- `assert_snapshot(page, mask_elements=list(SCREENSHOT_MASKS))` compares a screenshot with the approved one for that
  browser. `SCREENSHOT_MASKS`, in the pages package, lists what changes between runs; call `move_mouse_away()` first
  so no hover style shows. Make new screenshots with `--update-snapshots` in the runner image, look at each one, and
  commit them.
