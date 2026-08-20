const BASE_URL = "http://127.0.0.1:8000";
const WEB_APP_URL = "http://127.0.0.1:8000";
const GOOGLE_CLIENT_ID = "729764162601-988q3pc6rbhd6nmoa563j8opqgiiatvd.apps.googleusercontent.com";

document.addEventListener("DOMContentLoaded", () => {
  const loginSection = document.getElementById("login-section");
  const dashboardSection = document.getElementById("dashboard-section");
  const syncBadge = document.getElementById("sync-badge");
  const googleLoginBtn = document.getElementById("google-login-btn");
  const loginBtn = document.getElementById("login-btn");
  const logoutBtn = document.getElementById("logout-btn");
  const openWebPortalBtn = document.getElementById("open-web-portal-btn");
  const saveJobBtn = document.getElementById("save-job-btn");
  const statusMsg = document.getElementById("status-msg");
  const jobNote = document.getElementById("job-note");

  chrome.storage.local.get(["access_token"], (result) => {
    if (result && result.access_token) showDashboardSection();
    else showLoginSection();
  });

  // -------------------- Google Login --------------------
  if (googleLoginBtn) {
    googleLoginBtn.addEventListener("click", () => {
      const redirectUri = chrome.identity.getRedirectURL();
      const authUrl =
        "https://accounts.google.com/o/oauth2/v2/auth?" +
        "client_id=" + GOOGLE_CLIENT_ID + "&" +
        "response_type=token&" +
        "redirect_uri=" + encodeURIComponent(redirectUri) + "&" +
        "scope=" + encodeURIComponent("openid email profile");

      chrome.identity.launchWebAuthFlow(
        { url: authUrl, interactive: true },
        async (redirectUrl) => {
          if (chrome.runtime.lastError || !redirectUrl) {
            showStatus("Google login cancelled", "error");
            return;
          }

          const params = new URLSearchParams(new URL(redirectUrl).hash.substring(1));
          const googleAccessToken = params.get("access_token");
          if (!googleAccessToken) {
            showStatus("No Google token received", "error");
            return;
          }

          try {
            googleLoginBtn.disabled = true;
            showStatus("Authenticating...", "success");

            const res = await fetch(BASE_URL + "/api/auth/google", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ access_token: googleAccessToken }),
            });
            const data = await res.json();

            if (res.ok && data.access_token) {
              chrome.storage.local.set({ access_token: data.access_token }, () => {
                showStatus("Logged in with Google", "success");
                setTimeout(() => {
                  showDashboardSection();
                  showStatus("", "");
                }, 400);
              });
            } else {
              showStatus("Google verification failed", "error");
            }
          } catch (err) {
            showStatus("Server offline", "error");
          } finally {
            googleLoginBtn.disabled = false;
          }
        }
      );
    });
  }

  // -------------------- Email / Password Login --------------------
  if (loginBtn) {
    loginBtn.addEventListener("click", async () => {
      const email = document.getElementById("email")?.value.trim() || "";
      const password = document.getElementById("password")?.value.trim() || "";

      if (!email || !password) {
        showStatus("Email and password required", "error");
        return;
      }

      try {
        loginBtn.disabled = true;
        loginBtn.innerText = "Logging in...";

        const response = await fetch(BASE_URL + "/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });
        const data = await response.json();

        if (response.ok && data.access_token) {
          chrome.storage.local.set({ access_token: data.access_token }, () => {
            showStatus("Logged in successfully", "success");
            setTimeout(() => {
              showDashboardSection();
              showStatus("", "");
            }, 400);
          });
        } else {
          showStatus(data.detail || "Invalid credentials", "error");
        }
      } catch (err) {
        showStatus("Server offline", "error");
      } finally {
        loginBtn.disabled = false;
        loginBtn.innerText = "Login to Account";
      }
    });
  }

  // -------------------- Save this job (ANY site + tab title fallback) --------------------
  if (saveJobBtn) {
    saveJobBtn.addEventListener("click", async () => {
      const stored = await chrome.storage.local.get("access_token");
      const access_token = stored.access_token;

      if (!access_token) {
        showStatus("Login first", "error");
        return;
      }

      const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
      const tab = tabs[0];

      if (
        !tab ||
        !tab.id ||
        !tab.url ||
        tab.url.startsWith("chrome://") ||
        tab.url.startsWith("chrome-extension://")
      ) {
        showStatus("Open a normal job page first", "error");
        return;
      }

      saveJobBtn.disabled = true;
      saveJobBtn.innerText = "Saving...";
      showStatus("Reading page...", "success");

      try {
        let scraped = null;

        try {
          scraped = await chrome.tabs.sendMessage(tab.id, {
            action: "extract_job_data",
          });
        } catch (e1) {
          try {
            await chrome.scripting.executeScript({
              target: { tabId: tab.id },
              files: ["content.js"],
            });
            scraped = await chrome.tabs.sendMessage(tab.id, {
              action: "extract_job_data",
            });
          } catch (e2) {
            scraped = null;
          }
        }

        let title = (scraped && scraped.title) || "";
        let company = (scraped && scraped.company) || "";
        let locationVal = (scraped && scraped.location) || null;
        let source = (scraped && scraped.source) || "Other";
        const salary = (scraped && scraped.salary) || null;
        const experience_level = (scraped && scraped.experience_level) || null;
        const work_type = (scraped && scraped.work_type) || null;

        // Tab title fallback: "Python Engineer (Remote) | Hired | LinkedIn"
        if (!title || title === "Untitled job" || !company || company === "Unknown") {
          const tabTitle = (tab.title || "").trim();
          const parts = tabTitle
            .split("|")
            .map((p) => p.trim())
            .filter(Boolean);

          if ((!title || title === "Untitled job") && parts[0] && !/^linkedin$/i.test(parts[0])) {
            title = parts[0];
          }
          if ((!company || company === "Unknown") && parts[1] && !/^linkedin$/i.test(parts[1])) {
            company = parts[1];
          }
        }

        if (/linkedin\.com/i.test(tab.url)) source = "LinkedIn";
        else if (/indeed\.com/i.test(tab.url)) source = "Indeed";
        else if (/glassdoor\.com/i.test(tab.url)) source = "Glassdoor";
        else if (/wellfound\.com|angel\.co/i.test(tab.url)) source = "Wellfound";

        const payload = {
          title: (title || "Untitled job").toString().slice(0, 200),
          company: company || "Unknown",
          location: locationVal,
          job_url: (scraped && scraped.job_url) || tab.url,
          source: source,
          status: (scraped && scraped.status) || "Saved",
          notes: jobNote?.value.trim() || null,
          salary,
          experience_level,
          work_type,
        };

        const res = await fetch(BASE_URL + "/api/jobs/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + access_token,
          },
          body: JSON.stringify(payload),
        });

        if (res.ok) {
          showStatus("Saved: " + payload.title.slice(0, 40), "success");
          if (jobNote) jobNote.value = "";
        } else if (res.status === 401) {
          showStatus("Session expired — login again", "error");
        } else {
          let msg = "Save failed";
          try {
            const err = await res.json();
            if (err.detail) msg = String(err.detail);
          } catch (_) {}
          showStatus(msg, "error");
        }
      } catch (err) {
        console.error(err);
        showStatus("Could not read this page / server offline", "error");
      } finally {
        saveJobBtn.disabled = false;
        saveJobBtn.innerText = "Save this job";
      }
    });
  }

  // -------------------- Open web dashboard --------------------
  if (openWebPortalBtn) {
    openWebPortalBtn.addEventListener("click", () => {
      chrome.storage.local.get(["access_token"], (result) => {
        const t = result.access_token || "";
        const targetUrl = t
          ? WEB_APP_URL + "/?token=" + encodeURIComponent(t)
          : WEB_APP_URL;
        chrome.tabs.create({ url: targetUrl });
      });
    });
  }

  // -------------------- Logout --------------------
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      chrome.storage.local.remove(["access_token"], () => {
        showLoginSection();
        showStatus("Logged out", "error");
      });
    });
  }

  function showLoginSection() {
    if (loginSection) loginSection.classList.remove("hidden");
    if (dashboardSection) dashboardSection.classList.add("hidden");
    if (syncBadge) syncBadge.classList.add("hidden");
  }

  function showDashboardSection() {
    if (loginSection) loginSection.classList.add("hidden");
    if (dashboardSection) dashboardSection.classList.remove("hidden");
    if (syncBadge) syncBadge.classList.remove("hidden");
  }

  function showStatus(msg, type) {
    if (!statusMsg) return;
    statusMsg.innerText = msg || "";
    statusMsg.className = type || "";
  }
});