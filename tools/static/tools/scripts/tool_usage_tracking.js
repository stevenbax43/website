(() => {
  const toolCodes = {
    eenhedenconversie: "A2",
    drukverlies: "W3",
    thermisch_vermogen: "W6",
    driefase_vermogen: "E1",
  };
  const config = window.toolUsageTrackingConfig;
  const tool = config && toolCodes[config.tool];
  if (!tool) return;

  let logTimer;

  function recordCalculation() {
    const csrfToken = document.querySelector(
      'input[name="csrfmiddlewaretoken"]',
    )?.value;
    if (!csrfToken) {
      console.error("Could not record tool usage: CSRF token is unavailable.");
      return;
    }

    fetch(config.endpoint, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "X-CSRFToken": csrfToken,
      },
      body: new URLSearchParams({ tool }),
      keepalive: true,
    }).then(response => {
      if (!response.ok) {
        console.error(
          `Could not record tool usage: server returned ${response.status}.`,
        );
      }
    }).catch(error => {
      console.error("Could not record tool usage.", error);
    });
  }

  function scheduleCalculationLog(event) {
    if (!event.target.matches(
      'input:not([type="hidden"]):not([type="button"]):not([type="submit"]), select, textarea',
    )) {
      return;
    }

    window.clearTimeout(logTimer);
    logTimer = window.setTimeout(recordCalculation, 1000);
  }

  document.addEventListener("input", scheduleCalculationLog);
  document.addEventListener("change", scheduleCalculationLog);
})();
