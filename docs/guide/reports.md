# Read the reports

Each CI run on a pull request or on `main` keeps these, per browser:

| Report                        | Where                                                         | Good for                                   |
| ----------------------------- | ------------------------------------------------------------- | ------------------------------------------ |
| JUnit XML                     | the `reports-<browser>` artifact, `junit-<browser>.xml`       | tools that read test results               |
| pytest-html                   | the `reports-<browser>` artifact, `report-<browser>.html`     | one file to open in a browser              |
| Allure results                | the `allure-results-<browser>` artifact                       | building an Allure report yourself         |
| Traces, videos, screenshots   | the `test-results-<browser>` artifact, only when a test fails | seeing exactly what went wrong             |

## Allure

On `main`, CI merges the three browsers' results into one Allure 3 report and publishes it with these docs, at
[report/](../report/). The report keeps the history of the last 30 runs, so it shows trends and marks flaky tests.

To build one yourself from an `allure-results` folder:

```bash
npx allure@3.22.1 generate allure-results --config allurerc.json --output allure-report
npx allure@3.22.1 open allure-report
```

## Traces

A failed test keeps a Playwright trace: every action, the page before and after it, the network and the console. Open
it with:

```bash
uv run playwright show-trace test-results/<test-name>/trace.zip
```

or drop the file on [trace.playwright.dev](https://trace.playwright.dev/), which reads it in your browser.

## Screenshot failures

When a screenshot does not match, `test-results/snapshot-failures/` holds the actual image, the approved one and a
diff that marks each changed pixel.
