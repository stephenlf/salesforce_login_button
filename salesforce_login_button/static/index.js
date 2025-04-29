/** @param {{ model: DOMWidgetModel, el: HTMLElement }} context */

function render({ model, el }) {
  const buttonText = model.get('button_text') ?? 'Log in to Salesforce';
  const loginUrl = model.get('login_url');

  const button = document.createElement("button");
  button.textContent = buttonText;
  el.appendChild(button);

  button.onclick = () => {
    // Set up an event listenter to receive the auth information from the
    // popup window
    window.addEventListener('message', (event) => {
      if (event.origin !== window.location.origin) {
        console.error('Origin not allowed: ', event.origin);
        return;
      }

      const token = event.data;
      model.set('token', token);
      model.set('connected', true);
      model.save_changes();

    }, { once: true });

    // Open the login URL in a new window
    window.open(loginUrl, '_blank', 'width=400,height=400');
  }
}

export default { render };