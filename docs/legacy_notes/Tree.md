├── .builder
│ └── rules
│ ├── deploy-app.mdc
│ └── organize-ui.mdc
├── .dockerignore
├── .env
├── .gitignore
├── .npmrc
├── .prettierrc
├── AGENTS.md
├── backend
│ ├── .env
│ ├── api
│ │ ├── admin.py
│ │ ├── apps.py
│ │ ├── certificate_api.py
│ │ ├── email.py
│ │ ├── email_utils.py
│ │ ├── forms.py
│ │ ├── migrations
│ │ │ ├── 0001_initial.py
│ │ │ ├── **init**.py
│ │ │ └── **pycache**
│ │ │ ├── 0001_initial.cpython-310.pyc
│ │ │ ├── 0001_initial.cpython-313.pyc
│ │ │ ├── 0002_programa.cpython-313.pyc
│ │ │ ├── **init**.cpython-310.pyc
│ │ │ └── **init**.cpython-313.pyc
│ │ ├── models.py
│ │ ├── qr_views.py
│ │ ├── serializers.py
│ │ ├── serializers_ext.py
│ │ ├── templates
│ │ │ ├── api
│ │ │ │ ├── certificate
│ │ │ │ │ └── asistencia.html
│ │ │ │ ├── email
│ │ │ │ │ └── confirmacion.html
│ │ │ │ ├── email_acreditacion.html
│ │ │ │ ├── home.html
│ │ │ │ ├── landing.html
│ │ │ │ ├── register_group.html
│ │ │ │ ├── register_individual.html
│ │ │ │ └── registration_success.html
│ │ │ └── base.html
│ │ ├── tests.py
│ │ ├── urls.py
│ │ ├── views.py
│ │ ├── viewsets.py
│ │ ├── views_home.py
│ │ ├── **init**.py
│ │ └── **pycache**
│ │ ├── admin.cpython-310.pyc
│ │ ├── apps.cpython-310.pyc
│ │ ├── email.cpython-310.pyc
│ │ ├── email.cpython-313.pyc
│ │ ├── models.cpython-310.pyc
│ │ ├── qr_views.cpython-310.pyc
│ │ ├── serializers.cpython-310.pyc
│ │ ├── serializers.cpython-313.pyc
│ │ ├── urls.cpython-310.pyc
│ │ ├── urls.cpython-313.pyc
│ │ ├── views.cpython-310.pyc
│ │ ├── views.cpython-313.pyc
│ │ └── **init**.cpython-310.pyc
│ ├── API_DOC.md
│ ├── certificates
│ │ └── certificado_dgimenez.developergmail.com.pdf
│ ├── core
│ │ ├── asgi.py
│ │ ├── settings.py
│ │ ├── urls.py
│ │ ├── views_home.py
│ │ ├── wsgi.py
│ │ ├── **init**.py
│ │ └── **pycache**
│ │ ├── settings.cpython-310.pyc
│ │ ├── urls.cpython-310.pyc
│ │ ├── views_home.cpython-310.pyc
│ │ ├── wsgi.cpython-310.pyc
│ │ └── **init**.cpython-310.pyc
│ ├── db.sqlite3
│ ├── manage.py
│ ├── media
│ │ └── certificados
│ │ ├── certificado_Dario_Gimenez_32522833.pdf
│ │ ├── certificado_Dario_Gimenez_32522833_ESMdLB0.pdf
│ │ └── certificado_Dario_Gimenez_32522833_yQ5UGuL.pdf
│ ├── qr_codes
│ │ └── qr_dgimenez.developergmail.com.png
│ ├── requirements.txt
│ └── test_email.py
├── client
│ ├── App.tsx
│ ├── components
│ │ ├── CongressLogo.tsx
│ │ ├── data
│ │ │ └── logos.ts
│ │ ├── ImageSlider.tsx
│ │ ├── Layout.tsx
│ │ ├── LogoCarouselsSection.tsx
│ │ ├── LogoMarquee.tsx
│ │ ├── MobileNav.tsx
│ │ ├── ModernFadeSlider.tsx
│ │ ├── TruckCarousel.tsx
│ │ └── ui
│ │ ├── accordion.tsx
│ │ ├── alert-dialog.tsx
│ │ ├── alert.tsx
│ │ ├── aspect-ratio.tsx
│ │ ├── avatar.tsx
│ │ ├── badge.tsx
│ │ ├── breadcrumb.tsx
│ │ ├── button.tsx
│ │ ├── calendar.tsx
│ │ ├── card.tsx
│ │ ├── carousel.tsx
│ │ ├── chart.tsx
│ │ ├── checkbox.tsx
│ │ ├── collapsible.tsx
│ │ ├── command.tsx
│ │ ├── context-menu.tsx
│ │ ├── dialog.tsx
│ │ ├── drawer.tsx
│ │ ├── dropdown-menu.tsx
│ │ ├── form.tsx
│ │ ├── hover-card.tsx
│ │ ├── input-otp.tsx
│ │ ├── input.tsx
│ │ ├── label.tsx
│ │ ├── menubar.tsx
│ │ ├── navigation-menu.tsx
│ │ ├── pagination.tsx
│ │ ├── popover.tsx
│ │ ├── progress.tsx
│ │ ├── radio-group.tsx
│ │ ├── resizable.tsx
│ │ ├── scroll-area.tsx
│ │ ├── select.tsx
│ │ ├── separator.tsx
│ │ ├── sheet.tsx
│ │ ├── sidebar.tsx
│ │ ├── skeleton.tsx
│ │ ├── slider.tsx
│ │ ├── sonner.tsx
│ │ ├── switch.tsx
│ │ ├── table.tsx
│ │ ├── tabs.tsx
│ │ ├── textarea.tsx
│ │ ├── toast.tsx
│ │ ├── toaster.tsx
│ │ ├── toggle-group.tsx
│ │ ├── toggle.tsx
│ │ ├── tooltip.tsx
│ │ └── use-toast.ts
│ ├── global.css
│ ├── hooks
│ │ ├── use-mobile.tsx
│ │ └── use-toast.ts
│ ├── INTEGRACION_BACKEND.md
│ ├── lib
│ │ ├── api.ts
│ │ ├── utils.spec.ts
│ │ └── utils.ts
│ ├── pages
│ │ ├── CheckInPage.tsx
│ │ ├── Contacto.tsx
│ │ ├── Empresas.tsx
│ │ ├── EscaneoQR.tsx
│ │ ├── GenerarQRs.tsx
│ │ ├── HistoriaCampus.tsx
│ │ ├── Index.tsx
│ │ ├── NotFound.tsx
│ │ ├── PlaceholderPage.tsx
│ │ ├── Ponentes.tsx
│ │ ├── Programa.tsx
│ │ ├── Registro.tsx
│ │ ├── RegistroGrupal.tsx
│ │ ├── RegistroRapido.tsx
│ │ ├── SeleccionRegistro.tsx
│ │ ├── SobreElCongreso.tsx
│ │ └── VerificarDNI.tsx
│ └── vite-env.d.ts
├── components.json
├── CONFIGURACION_EMAIL.md
├── index.html
├── netlify.toml
├── package-lock.json
├── package.json
├── pnpm-lock.yaml
├── postcss.config.js
├── README.md
├── recrear_db.sh
├── shared
│ └── api.ts
├── SISTEMA_QR_NUEVO.md
├── tailwind.config.ts
├── TODO.md
├── tsconfig.json
├── vite.config.server.ts
└── vite.config.ts
