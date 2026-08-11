USER_VERIFICATION_MAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />

  <style>
    body {
      margin: 0;
      padding: 0;
      background-color: #f5f7fb;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
        Helvetica, Arial, sans-serif;
      color: #1f2937;
    }

    table {
      border-spacing: 0;
      border-collapse: collapse;
    }

    img {
      border: 0;
      display: block;
    }

    .wrapper {
      width: 100%;
      background-color: #f5f7fb;
      padding: 48px 16px;
    }

    .container {
      width: 100%;
      max-width: 560px;
      margin: 0 auto;
      background-color: #ffffff;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 4px 20px rgba(15, 23, 42, 0.06);
    }

    .header {
      padding: 32px 40px 24px;
      text-align: center;
      border-bottom: 1px solid #eef0f4;
    }

    .logo {
      display: inline-block;
      font-size: 22px;
      font-weight: 700;
      color: #111827;
      text-decoration: none;
      letter-spacing: -0.4px;
    }

    .logo-dot {
      color: #6366f1;
    }

    .content {
      padding: 40px;
    }

    .icon-wrapper {
      width: 64px;
      height: 64px;
      margin: 0 auto 24px;
      background-color: #eef2ff;
      border-radius: 50%;
      text-align: center;
    }

    .icon {
      font-size: 30px;
      line-height: 64px;
    }

    .title {
      margin: 0 0 16px;
      text-align: center;
      font-size: 28px;
      line-height: 36px;
      font-weight: 700;
      letter-spacing: -0.6px;
      color: #111827;
    }

    .greeting {
      margin: 0 0 16px;
      font-size: 16px;
      line-height: 26px;
      color: #374151;
    }

    .description {
      margin: 0 0 28px;
      font-size: 16px;
      line-height: 26px;
      color: #6b7280;
    }

    .button-wrapper {
      text-align: center;
      padding: 4px 0 28px;
    }

    .button {
      display: inline-block;
      background-color: #4f46e5;
      color: #ffffff !important;
      text-decoration: none;
      font-size: 16px;
      font-weight: 600;
      line-height: 24px;
      padding: 13px 28px;
      border-radius: 9px;
    }

    .expiry {
      margin: 0;
      padding: 16px;
      background-color: #f9fafb;
      border-radius: 8px;
      font-size: 13px;
      line-height: 20px;
      color: #6b7280;
      text-align: center;
    }

    .fallback {
      margin: 28px 0 0;
      font-size: 13px;
      line-height: 20px;
      color: #9ca3af;
    }

    .url {
      display: block;
      margin-top: 8px;
      padding: 10px;
      background-color: #f9fafb;
      border: 1px solid #eef0f4;
      border-radius: 6px;
      color: #6366f1;
      word-break: break-all;
      font-size: 12px;
    }

    .footer {
      padding: 24px 40px 32px;
      text-align: center;
      border-top: 1px solid #eef0f4;
    }

    .footer-text {
      margin: 0;
      font-size: 12px;
      line-height: 20px;
      color: #9ca3af;
    }

    .footer-link {
      color: #6366f1;
      text-decoration: none;
    }

    @media only screen and (max-width: 600px) {
      .wrapper {
        padding: 24px 12px;
      }

      .header {
        padding: 24px 24px 20px;
      }

      .content {
        padding: 32px 24px;
      }

      .footer {
        padding: 20px 24px 28px;
      }

      .title {
        font-size: 24px;
        line-height: 32px;
      }

      .button {
        display: block;
        width: auto;
      }
    }
  </style>
</head>

<body>
  <table
    role="presentation"
    width="100%"
    cellpadding="0"
    cellspacing="0"
    border="0"
  >
    <tr>
      <td class="wrapper">

        <table
          role="presentation"
          class="container"
          cellpadding="0"
          cellspacing="0"
          border="0"
          align="center"
        >

          <!-- Header -->
          <tr>
            <td class="header">
              <a href="{{app_url}}" class="logo">
                {{app_name}}<span class="logo-dot">.</span>
              </a>
            </td>
          </tr>

          <!-- Content -->
          <tr>
            <td class="content">

              <div class="icon-wrapper">
                <span class="icon">✉️</span>
              </div>

              <h1 class="title">
                Verify your email
              </h1>

              <p class="greeting">
                Hi {{user_name}},
              </p>

              <p class="description">
                Thanks for creating an account with {{app_name}}.
                Please verify your email address to finish setting up
                your account.
              </p>

              <div class="button-wrapper">
                <a
                  href="{{verification_url}}"
                  class="button"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Verify my email
                </a>
              </div>

              <p class="expiry">
                This verification link will expire in
                <strong>{{expiry_time}}</strong>.
              </p>

              <p class="fallback">
                If the button above doesn't work, copy and paste this
                link into your browser:
              </p>

              <div class="url">
                {{verification_url}}
              </div>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td class="footer">

              <p class="footer-text">
                If you didn't create an account with {{app_name}},
                you can safely ignore this email.
              </p>

              <p class="footer-text" style="margin-top: 8px;">
                © {{year}} {{app_name}}. All rights reserved.
              </p>

            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>
</body>
</html>
"""

RESET_PASSWORD_MAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />

  <style>
    body {
      margin: 0;
      padding: 0;
      background-color: #f5f7fb;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
        Helvetica, Arial, sans-serif;
      color: #1f2937;
    }

    table {
      border-spacing: 0;
      border-collapse: collapse;
    }

    img {
      border: 0;
      display: block;
    }

    .wrapper {
      width: 100%;
      background-color: #f5f7fb;
      padding: 48px 16px;
    }

    .container {
      width: 100%;
      max-width: 560px;
      margin: 0 auto;
      background-color: #ffffff;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 4px 20px rgba(15, 23, 42, 0.06);
    }

    .header {
      padding: 32px 40px 24px;
      text-align: center;
      border-bottom: 1px solid #eef0f4;
    }

    .logo {
      display: inline-block;
      font-size: 22px;
      font-weight: 700;
      color: #111827;
      text-decoration: none;
      letter-spacing: -0.4px;
    }

    .logo-dot {
      color: #6366f1;
    }

    .content {
      padding: 40px;
    }

    .icon-wrapper {
      width: 64px;
      height: 64px;
      margin: 0 auto 24px;
      background-color: #eef2ff;
      border-radius: 50%;
      text-align: center;
    }

    .icon {
      font-size: 30px;
      line-height: 64px;
    }

    .title {
      margin: 0 0 16px;
      text-align: center;
      font-size: 28px;
      line-height: 36px;
      font-weight: 700;
      letter-spacing: -0.6px;
      color: #111827;
    }

    .greeting {
      margin: 0 0 16px;
      font-size: 16px;
      line-height: 26px;
      color: #374151;
    }

    .description {
      margin: 0 0 28px;
      font-size: 16px;
      line-height: 26px;
      color: #6b7280;
    }

    .button-wrapper {
      text-align: center;
      padding: 4px 0 28px;
    }

    .button {
      display: inline-block;
      background-color: #4f46e5;
      color: #ffffff !important;
      text-decoration: none;
      font-size: 16px;
      font-weight: 600;
      line-height: 24px;
      padding: 13px 28px;
      border-radius: 9px;
    }

    .expiry {
      margin: 0;
      padding: 16px;
      background-color: #f9fafb;
      border-radius: 8px;
      font-size: 13px;
      line-height: 20px;
      color: #6b7280;
      text-align: center;
    }

    .fallback {
      margin: 28px 0 0;
      font-size: 13px;
      line-height: 20px;
      color: #9ca3af;
    }

    .url {
      display: block;
      margin-top: 8px;
      padding: 10px;
      background-color: #f9fafb;
      border: 1px solid #eef0f4;
      border-radius: 6px;
      color: #6366f1;
      word-break: break-all;
      font-size: 12px;
    }

    .footer {
      padding: 24px 40px 32px;
      text-align: center;
      border-top: 1px solid #eef0f4;
    }

    .footer-text {
      margin: 0;
      font-size: 12px;
      line-height: 20px;
      color: #9ca3af;
    }

    .footer-link {
      color: #6366f1;
      text-decoration: none;
    }

    @media only screen and (max-width: 600px) {
      .wrapper {
        padding: 24px 12px;
      }

      .header {
        padding: 24px 24px 20px;
      }

      .content {
        padding: 32px 24px;
      }

      .footer {
        padding: 20px 24px 28px;
      }

      .title {
        font-size: 24px;
        line-height: 32px;
      }

      .button {
        display: block;
        width: auto;
      }
    }
  </style>
</head>

<body>
  <table
    role="presentation"
    width="100%"
    cellpadding="0"
    cellspacing="0"
    border="0"
  >
    <tr>
      <td class="wrapper">

        <table
          role="presentation"
          class="container"
          cellpadding="0"
          cellspacing="0"
          border="0"
          align="center"
        >

          <!-- Header -->
          <tr>
            <td class="header">
              <a href="{{app_url}}" class="logo">
                {{app_name}}<span class="logo-dot">.</span>
              </a>
            </td>
          </tr>

          <!-- Content -->
          <tr>
            <td class="content">

              <div class="icon-wrapper">
                <span class="icon">✉️</span>
              </div>

              <h1 class="title">
                Reset Password
              </h1>

              <p class="greeting">
                Hi {{user_name}},
              </p>

              <p class="description">
                A Password Reset has been requested with this email on {{app_name}}.
                Please use the below button or link to reset your password. If you have not requested this, please ignore this email.
              </p>

              <div class="button-wrapper">
                <a
                  href="{{reset_password_url}}"
                  class="button"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Reset Password
                </a>
              </div>

              <p class="expiry">
                This password reset link will expire in
                <strong>{{expiry_time}}</strong>.
              </p>

              <p class="fallback">
                If the button above doesn't work, copy and paste this
                link into your browser:
              </p>

              <div class="url">
                {{reset_password_url}}
              </div>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td class="footer">

              <p class="footer-text">
                If you didn't create an account with {{app_name}},
                you can safely ignore this email.
              </p>

              <p class="footer-text" style="margin-top: 8px;">
                © {{year}} {{app_name}}. All rights reserved.
              </p>

            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>
</body>
</html>
"""
