# 📓 Changelog – FrancoUke / StrumSphere

All notable changes to this project will be documented in this file.

## [Unreleased]

- Planned: Social login (Google OAuth via django-allauth)
- Planned: Admin toggle to re-enable StrumSphere site
- Planned: Song like/favorite system per user

---

## [2025-06-09] – 🔐 Authentication Upgrades

### Added
- Custom user registration form using `CustomUserCreationForm`
- `CustomLoginView` supports site_name context
- Password reset system using Django's `auth_views`
  - Templates created:
    - `password_reset_form.html`
    - `password_reset_done.html`
    - `password_reset_confirm.html`
    - `password_reset_complete.html`
    - `password_reset_email.html`
    - `password_reset_subject.txt`

### Changed
- Replaced default `UserCreationForm` with custom form wired to `CustomUser`
- All password reset views now use namespaced reverse URLs: `'users:password_reset_*'`
- Set `success_url` explicitly with `reverse_lazy` to avoid reverse errors

### Fixed
- `NoReverseMatch` errors on password reset views due to missing `success_url`
- 500 error caused by duplicate `password_reset/` paths in `users/urls.py`
- Middleware misconfiguration: `DisableStrumSphereMiddleware` incorrectly placed in `INSTALLED_APPS`

---

## [2025-06-08] – 🧱 Project Setup

### Added
- Project context established
- Initial review of custom apps: `users`, `songbook`, `tools`
- Multi-site routing: `FrancoUke` (active), `StrumSphere` (middleware-disabled)
- Custom user model (`users.CustomUser`) and user preference system

---

