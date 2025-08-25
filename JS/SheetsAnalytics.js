// File: SheetsAnalytics.js
// Path: OurLibrary/JS/SheetsAnalytics.js
// Standard: AIDEV-PascalCase-2.3
// Created: 2025-08-25
// Last Modified: 2025-08-25  01:00PM
// Symlink Pattern: PROJECT_TOOL
//
// Description: Minimal client logger to the three Phase‑2 Sheets.
// Uses Google's JS client (auth present in project) and appends rows.
// Sheet IDs taken from Phase‑2 spec.

const SHEETS = {
  registrations: '1lhdKnjyltHHQaDSfAfQ9Vcog40vsnFTqzDFxa9sEBFE',
  incomplete:   '197Qu-GeIYaL2CyiFArhgM9GJbuyGCUK4JZjxWXsAHaI',
  sessions:     '1KZPSyXCqkWKHzaM8Y45BmoZqHpzU-VWOpQq0W8UELxg'
};

async function appendRow(sheetId, values) {
  // assumes gapi client is loaded & authorized via your existing OAuth flow
  return gapi.client.sheets.spreadsheets.values.append({
    spreadsheetId: sheetId,
    range: 'A1',
    valueInputOption: 'USER_ENTERED',
    insertDataOption: 'INSERT_ROWS',
    resource: { values: [values] }
  });
}

// Public API
export async function logRegistration({
  userId = '', email = '', fullName = '', method = '',
  status = '', code = '', zip = '', terms = false,
  device = navigator.userAgent, sessionId = '', referrer = document.referrer,
  duration = '', notes = ''
}) {
  const row = [
    new Date().toISOString(), userId, email, fullName, method, status,
    code, zip, terms ? 'TRUE' : 'FALSE', device, sessionId, referrer, duration, notes
  ];
  await appendRow(SHEETS.registrations, row);
}

export async function logIncompleteEmail({
  email = '', event = '', progress = '',
  sessionId = '', ua = navigator.userAgent, referrer = document.referrer,
  url = location.pathname, deviceType = (/Mobi|Android/i.test(navigator.userAgent) ? 'mobile' : 'desktop'),
  timeOnPage = '', exitPoint = '', followUp = 'not_contacted'
}) {
  const row = [
    new Date().toISOString(), email, event, progress, sessionId,
    ua, referrer, url, deviceType, timeOnPage, exitPoint, followUp
  ];
  await appendRow(SHEETS.incomplete, row);
}

export async function logSession({
  userId = '', email = '', actionType = '', details = {},
  book = '', search = '', sessionDuration = '', pageViews = '',
  device = navigator.userAgent, geo = '', conversion = '', engagement = ''
}) {
  const row = [
    new Date().toISOString(), userId, email, actionType, JSON.stringify(details),
    book, search, sessionDuration, pageViews, device, geo, conversion, engagement
  ];
  await appendRow(SHEETS.sessions, row);
}