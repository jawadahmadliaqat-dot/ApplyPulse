function clean(s) {
  return (s || "").replace(/\s+/g, " ").trim();
}

function extractFromDocumentTitle() {
  // LinkedIn usually: "Python Engineer (Remote) | Hired | LinkedIn"
  const raw = clean(document.title);
  if (!raw) return null;

  const parts = raw.split("|").map((p) => clean(p)).filter(Boolean);
  if (parts.length >= 2) {
    let title = parts[0];
    let company = parts[1];
    if (/^linkedin$/i.test(company)) company = parts[2] || "";
    if (/^linkedin$/i.test(title)) return null;
    return {
      title: title,
      company: /^linkedin$/i.test(company) ? "" : company,
    };
  }
  return { title: raw.replace(/\s*\|\s*LinkedIn$/i, ""), company: "" };
}

function firstText(selectors) {
  for (const sel of selectors) {
    try {
      const el = document.querySelector(sel);
      if (!el) continue;
      const t = clean(el.innerText || el.textContent);
      if (t && t.length > 1) return t;
    } catch (_) {}
  }
  return "";
}

function pageText() {
  return clean(document.body?.innerText || "").slice(0, 30000);
}

function extractSalary(text) {
  const match = text.match(/(?:\$|USD\s*)[\d,.]+\s*(?:k|K)?\s*(?:-|–|to)\s*(?:\$|USD\s*)?[\d,.]+\s*(?:k|K)?(?:\s*(?:per year|annually|\/yr|\/hour|per hour))?/i);
  return match ? clean(match[0]) : null;
}

function extractWorkType(text) {
  const match = text.match(/\b(remote|hybrid|on[- ]?site|onsite)\b/i);
  if (!match) return null;
  const value = match[1].toLowerCase().replace("on-site", "onsite");
  return value === "onsite" ? "Onsite" : value[0].toUpperCase() + value.slice(1);
}

function extractExperience(text) {
  const match = text.match(/\b(entry[- ]level|intern(ship)?|junior|mid[- ]level|senior|lead|principal|staff)\b/i);
  return match ? clean(match[1]).replace(/\b\w/g, (letter) => letter.toUpperCase()) : null;
}

function isPositionClosed(text) {
  return /(?:job|position|role|this posting)\s+(?:is\s+)?(?:closed|no longer available|expired|filled)|(?:no longer accepting applications)|(?:application deadline has passed)/i.test(text);
}

function extractJobFromPage() {
  const host = location.hostname.replace(/^www\./, "");
  let title = "";
  let company = "";
  let locationText = "";
  let source = "Other";
  const visibleText = pageText();

  if (host.includes("linkedin.com")) {
    source = "LinkedIn";

    // A) Best fallback for /jobs/view/ pages
    const fromTitle = extractFromDocumentTitle();
    if (fromTitle) {
      title = fromTitle.title;
      company = fromTitle.company;
    }

    // B) Visible DOM
    if (!title) {
      title = firstText([
        "h1",
        ".job-details-jobs-unified-top-card__job-title",
        ".jobs-unified-top-card__job-title",
        ".t-24",
      ]);
    }

    if (!company) {
      company = firstText([
        ".job-details-jobs-unified-top-card__company-name",
        ".jobs-unified-top-card__company-name",
        "a[href*='/company/']",
        ".artdeco-entity-lockup__subtitle",
      ]);
    }

    locationText = firstText([
      ".job-details-jobs-unified-top-card__bullet",
      ".jobs-unified-top-card__bullet",
      ".tvm__text",
    ]);

    // C) Body text near top (last resort)
    if (!title || title.length < 3) {
      const h = document.querySelector("h1");
      if (h) title = clean(h.innerText);
    }
  } else if (host.includes("indeed.com")) {
    source = "Indeed";
    title = firstText(["h1.jobsearch-JobInfoHeader-title", "h1"]);
    company = firstText(["[data-company-name='true']", "[data-testid='inlineHeader-companyName']"]);
    locationText = firstText(["[data-testid='inlineHeader-companyLocation']"]);
  } else {
    const og = document.querySelector('meta[property="og:title"]')?.content;
    title = clean(og) || firstText(["h1"]) || clean(document.title);
    company = clean(document.querySelector('meta[property="og:site_name"]')?.content) || host.split(".")[0];
    source = host;
  }

  title = clean(title);
  company = clean(company);
  if (/^linkedin$/i.test(company)) company = "";
  if (title.toLowerCase().includes("linkedin") && title.includes("|")) {
    title = clean(title.split("|")[0]);
  }

  return {
    title: title || "Untitled job",
    company: company || "Unknown",
    location: locationText || null,
    job_url: location.href,
    source: source,
    status: isPositionClosed(visibleText) ? "Position Closed" : "Saved",
    salary: extractSalary(visibleText),
    experience_level: extractExperience(visibleText),
    work_type: extractWorkType(visibleText),
  };
}

chrome.runtime.onMessage.addListener((req, _s, sendResponse) => {
  if (req.action === "extract_job_data" || req.action === "SCRAPE_JOB") {
    sendResponse(extractJobFromPage());
  }
  return true;
});