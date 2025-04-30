

import marimo

__generated_with = "0.13.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from salesforce_login_button.widget import SalesforceLoginButton
    return SalesforceLoginButton, mo


@app.cell
def _(SalesforceLoginButton):
    button = SalesforceLoginButton(domain='test', login_url='http://localhost:5000/login', )
    button
    return


@app.cell
def _(mo):
    mo.app_meta().request.user.display_name
    return


if __name__ == "__main__":
    app.run()
