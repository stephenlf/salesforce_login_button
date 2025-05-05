/** @param {{ model: DOMWidgetModel, el: HTMLElement }} context */

function render({ model, el }) {
  const buttonText = model.get('button_text') ?? 'Log in to Salesforce';
  const loginUrl = model.get('login_url');
  const domain = model.get('domain');
  const userId = model.get('user_id');

  const button = document.createElement("button");
  button.textContent = buttonText;
  el.appendChild(button);

  button.onclick = () => {
    // Set up an event listenter to receive the auth information from the
    // popup window
    console.log('running');
    const target = `${loginUrl}?domain=${domain}&user_id=${userId}`
    // Open the login URL in a new window
    window.open(target, '_blank', 'width=400,height=400');

    const postMessageHandler = (event) => {
      // if (event.origin !== window.location.origin) {
      //   console.error('Origin not allowed: ', event.origin);
      //   return;
      // }

      if (event.data.type == 'SALESFORCE_OAUTH') {
        window.removeEventListener('message', postMessageHandler);
        console.log(event);
        const token = event.data.payload;
        model.set('token', token);
        model.set('connected', true);
        model.save_changes();
      }
    };
    window.addEventListener('message', postMessageHandler);
  }
}

export default { render };