# Lee's EShop

A modern E-Commerce application built with Python and Django.

## Architecture

## DevOps Features

- [x] Isolated environment using Poetry and Dockerized images.
- [x] The Twelve-Factor App: using environment variables to control configurations.
- [x] Celery with RabbitMQ Broker & Redis Result Backend for queue processing.
- [x] Celery Flower for Celery control plane.
- [x] Docker Compose for local development.
- [ ] Live Chat Support using Django Channels over Websockets.
- [ ] Security checklist: CSRF / XSS / COOP / HSTS / ALLOWED_HOSTS / CORS / SQL Injections
- [ ] CI using Github Actions.
- [ ] HTTPS using Let's Encrypt's SSL.
- [x] RDB using PostgreSQL
- [x] Cache views and JSON responses using Redis
- [ ] Reversed Proxy using Nginx
- [ ] Web Server using Gunicorn
- [ ] Media Block Storage using S3
- [ ] Cloudflare for CDN & DDOS protection.
- [ ] Terraform for infrastructure provisioning.
- [ ] CD with Ansible.
- [ ] Monitoring & Observability using Promentheuse & Grafana stack

## Application Features

- [x] Admin Management UI using Django defaults.
- [x] Models: Product / Category / Cart / Coupon / Order / OrderItem / Payment / Customer (~) / Blog (~)
- [x] Order with discount
- [x] Products recommendation
- [x] Payment Gateway / Payment Webhook using Stripe.
- [x] PDF/CSV generation and sending emails (console).
- [ ] Rich Text Editor using CKE
- [ ] OAuth2 for AuthN/AuthZ (Auth0)
- [x] DRF for RestAPIs
- [ ] Automated Tests
- [x] i18n: VN/EN

## How-to

### Run The Shop Locally

### Deploy The Shop

## Contribute
