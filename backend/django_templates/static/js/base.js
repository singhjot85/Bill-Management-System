async function makeApiCall(base_url, method = "GET", data = null) {
  try {
    let url = base_url;
    const options = {
      method: method,
      headers: {
        "Content-Type": "application/json",
      },
    };

    if (data) {
      if (method !== "GET") {
        options.body = JSON.stringify(data);
      }
      else {
        const urlObj = new URL(base_url);
        Object.entries(data).forEach(([key, value]) => {
          urlObj.searchParams.append(key, value);
        });
        url = urlObj.toString();
      }
    }

    const response = await fetch(url, options);

    let responseData = {};
    try {
      responseData = await response.json();
    } catch {
      try {
        responseData = await response.text();
      }
      catch {
        responseData = null;
      }
    }

    if (!response.ok) {
      throw new Error(
        responseData.message ||
          responseData.detail ||
          `Request failed (${response.status})`,
      );
    }

    return {
      status: response.status,
      response: responseData,
      ok: true,
    };
  } catch (error) {
    showSnackbar(error.message || "Unexpected API error");
    return {
      status: 500,
      response: null,
      ok: false,
    };
  }
}

window.logoutUser = async function logoutUser() {
  await makeApiCall("api/auth/logout/", "GET");
  window.location.href = "/";
}
