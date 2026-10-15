/**
 * Congreso UNAB 2026 - Multiselect Filters Overlay
 * Transforma el panel de filtros de Django Admin en un sistema de checkboxes sumables interactivos
 * con iconos informativos "?" de ayuda educativa para el usuario.
 */
document.addEventListener("DOMContentLoaded", () => {
    const filterPanel = document.getElementById("changelist-filter");
    if (!filterPanel) return;

    // --- 1. CONFIGURACIÓN DE TOOLTIPS EDUCATIVOS (SIGNOS DE PREGUNTA ?) ---
    const tooltipTexts = {
        "estado dni": "Permite segmentar a los asistentes según si ya cargaron un DNI de 8 dígitos numéricos válidos o si aún tienen su documento en blanco o incompleto.",
        "institución": "Filtra por la entidad educativa o laboral ingresada en la ficha del asistente (ej: UNaB, otras universidades o empresas).",
        "carrera / cargo": "Agrupa a los asistentes según la carrera que estudian/dictan o el cargo profesional que declararon al registrarse.",
        "pertenecía unab": "Identifica rápidamente a los miembros internos de la comunidad (estudiantes y docentes de la Universidad Nacional de Almirante Brown) vs. externos.",
        "asistencia (edición activa)": "Filtra en tiempo real a los inscritos que ya acreditaron su ingreso al predio mediante el escaneo de su código QR personal vs. los que están pendientes.",
        "tipo de perfil": "Filtra por el rol asignado al participante: Estudiante, Docente, Graduado, Profesional, Prensa, Visitante, etc.",
        "año de la edición": "Permite visualizar y comparar registros históricos cruzando diferentes ediciones del congreso (2024, 2025, 2026).",
        "registrado el": "Filtra a los asistentes según el rango de días o semanas en que realizaron su inscripción.",
        "estado": "Controla el estado del workflow del elemento (ej: Pendiente, Bases Enviadas, Pendiente de Pago, Confirmado, Rechazado).",
        "¿es patrocinador?": "Filtra entre empresas patrocinadoras (Sponsors) y participantes regulares de la exposición.",
        "¿participó en la edición anterior?": "Segmenta las empresas expositoras recurrentes que estuvieron en la edición pasada, ideal para fidelización.",
        "tipo de certificado": "Filtra los certificados generados según su categoría: Asistencia regular, Disertante o Corporativo de Empresa."
    };

    // Inyectar Estilos CSS Premium para los Checkboxes, Tooltips e Iconos "?"
    const styleEl = document.createElement("style");
    styleEl.innerHTML = `
        /* Contenedor de filtros */
        #changelist-filter {
            background: #0d061c !important;
            border-left: 1px solid rgba(167, 139, 250, 0.15) !important;
            padding: 15px !important;
        }
        #changelist-filter h2 {
            background: linear-gradient(135deg, #a78bfa, #06b6d4) !important;
            color: #0d061c !important;
            font-weight: 800 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
            border-radius: 8px !important;
            padding: 10px !important;
            margin-bottom: 15px !important;
            font-size: 13px !important;
            text-align: center !important;
        }
        #changelist-filter h3 {
            color: #a78bfa !important;
            font-size: 11px !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px !important;
            margin-top: 15px !important;
            margin-bottom: 8px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
            padding-bottom: 4px !important;
        }

        /* Icono de Ayuda Educativo "?" */
        .help-icon-badge {
            background: rgba(167, 139, 250, 0.1) !important;
            border: 1px solid rgba(167, 139, 250, 0.25) !important;
            color: #06b6d4 !important;
            width: 16px !important;
            height: 16px !important;
            border-radius: 50% !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 10px !important;
            font-weight: bold !important;
            cursor: pointer !important;
            position: relative !important;
            transition: all 0.2s ease !important;
        }
        .help-icon-badge:hover {
            background: #06b6d4 !important;
            color: #0d061c !important;
            box-shadow: 0 0 8px #06b6d4;
            transform: scale(1.1);
        }

        /* Tooltip Flotante Estilizado */
        .help-icon-badge .tooltip-text {
            visibility: hidden;
            width: 180px;
            background: #0f0724;
            border: 1px solid rgba(6, 182, 212, 0.4);
            color: #e2e8f0;
            text-align: left;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 10px;
            font-weight: 500;
            line-height: 1.4;
            text-transform: none;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.6);
            
            /* Posicionamiento */
            position: absolute;
            z-index: 99999;
            right: 24px;
            top: -20px;
            opacity: 0;
            transition: opacity 0.3s ease, transform 0.3s ease;
            transform: translateX(-5px);
            pointer-events: none;
        }
        .help-icon-badge:hover .tooltip-text {
            visibility: visible;
            opacity: 1;
            transform: translateX(0);
        }

        /* Elementos del listado de filtros */
        #changelist-filter ul {
            margin-left: 0 !important;
            padding-left: 0 !important;
            list-style: none !important;
        }
        #changelist-filter li {
            margin-bottom: 5px !important;
            padding-left: 0 !important;
            display: flex !important;
            align-items: center !important;
        }
        .filter-checkbox-container {
            display: flex !important;
            align-items: center !important;
            gap: 8px !important;
            width: 100% !important;
            cursor: pointer !important;
            padding: 4px 8px !important;
            border-radius: 6px !important;
            transition: all 0.2s ease !important;
        }
        .filter-checkbox-container:hover {
            background: rgba(255, 255, 255, 0.03) !important;
        }
        .filter-checkbox-container.selected {
            background: rgba(167, 139, 250, 0.08) !important;
        }
        .filter-checkbox-container input[type="checkbox"] {
            cursor: pointer !important;
            accent-color: #06b6d4 !important;
            width: 14px !important;
            height: 14px !important;
        }
        .filter-checkbox-container span {
            font-size: 11.5px !important;
            color: #cbd5e1 !important;
            font-weight: 500 !important;
        }
        .filter-checkbox-container.selected span {
            color: #fff !important;
            font-weight: 600 !important;
        }

        /* Botón Flotante de Aplicar Segmentación */
        .btn-apply-filters-floating {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: linear-gradient(135deg, #06b6d4, #3b82f6);
            color: #fff !important;
            border: none;
            padding: 12px 24px;
            border-radius: 30px;
            font-weight: 700;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 0 20px rgba(6, 182, 212, 0.5);
            cursor: pointer;
            z-index: 10000;
            display: none;
            align-items: center;
            gap: 8px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(255, 255, 255, 0.15);
        }
        .btn-apply-filters-floating:hover {
            transform: translateY(-3px) scale(1.05);
            box-shadow: 0 0 30px rgba(6, 182, 212, 0.8);
        }
        .btn-apply-filters-floating.visible {
            display: flex !important;
            animation: bounceIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        @keyframes bounceIn {
            0% { transform: translateY(50px) scale(0.8); opacity: 0; }
            100% { transform: translateY(0) scale(1); opacity: 1; }
        }
    `;
    document.head.appendChild(styleEl);

    // --- 2. PARSEAR URL ACTUAL Y PARÁMETROS GET ---
    const currentParams = new URLSearchParams(window.location.search);
    const activeFilters = {};

    // Cargar parámetros GET activos
    for (const [key, value] of currentParams.entries()) {
        activeFilters[key] = value.split(","); // Soporte de multiselect previo
    }

    // Estructura para registrar los cambios interactivos locales
    const filterState = JSON.parse(JSON.stringify(activeFilters));

    // --- 3. RECORRER Y RECONSTRUIR CADA BLOQUE DE FILTROS ---
    const filterHeaders = filterPanel.querySelectorAll("h3");
    let changedState = false;

    // Crear el Botón Flotante
    const applyButton = document.createElement("button");
    applyButton.type = "button";
    applyButton.className = "btn-apply-filters-floating";
    applyButton.innerHTML = "<span>Aplicar Segmentación ⚡</span>";
    document.body.appendChild(applyButton);

    applyButton.addEventListener("click", () => {
        // Reconstruir URL
        const newParams = new URLSearchParams();
        
        // Conservar parámetros ajenos a los filtros del listado si los hay (p. ej. 'q' para búsqueda)
        for (const [key, value] of currentParams.entries()) {
            if (!key.startsWith("ot_") && key !== "q" && key !== "o" && key !== "p") {
                // Parámetros de ordenación (o), paginación (p) y búsqueda (q) se conservan, 
                // pero los filtros los actualizaremos con el nuevo filterState
                continue;
            }
            newParams.set(key, value);
        }

        // Agregar filtros del filterState
        for (const [key, values] of Object.entries(filterState)) {
            const cleanValues = values.filter(v => v !== "" && v !== "all");
            if (cleanValues.length > 0) {
                newParams.set(key, cleanValues.join(","));
            }
        }

        // Navegar a la nueva URL
        window.location.search = newParams.toString();
    });

    filterHeaders.forEach(header => {
        const titleText = header.innerText.trim().toLowerCase();
        
        // A) Inyectar Icono "?" Educativo si hay texto explicativo configurado
        const descText = tooltipTexts[titleText] || `Filtra el listado de registros agrupando por el campo ${titleText.toUpperCase()}.`;
        
        const helpBadge = document.createElement("span");
        helpBadge.className = "help-icon-badge";
        helpBadge.innerText = "?";
        
        const tooltip = document.createElement("span");
        tooltip.className = "tooltip-text";
        tooltip.innerText = descText;
        
        helpBadge.appendChild(tooltip);
        header.appendChild(helpBadge);

        // B) Convertir Lista en Checkboxes Sumables
        const list = header.nextElementSibling;
        if (list && list.tagName === "UL") {
            const items = list.querySelectorAll("li");
            
            // Detectar cuál es el parámetro GET asociado a este bloque de filtros
            let filterKey = null;
            let hasAllOption = false;

            items.forEach(item => {
                const link = item.querySelector("a");
                if (!link) return;
                
                const href = link.getAttribute("href");
                const urlParams = new URLSearchParams(href.split("?")[1] || "");
                
                // Encontrar la llave del filtro
                for (const key of urlParams.keys()) {
                    if (key !== "e" && key !== "o" && key !== "p") {
                        filterKey = key;
                        break;
                    }
                }
            });

            if (!filterKey) return;

            // Re-renderizar opciones
            items.forEach(item => {
                const link = item.querySelector("a");
                if (!link) return;

                const label = link.innerText.trim();
                const href = link.getAttribute("href");
                const urlParams = new URLSearchParams(href.split("?")[1] || "");
                const val = urlParams.get(filterKey) || "all";

                const isAllOption = val === "all" || href === "?" || !urlParams.has(filterKey);
                
                // Determinar si está seleccionado leyendo de filterState
                const isChecked = filterState[filterKey] 
                    ? filterState[filterKey].includes(val) 
                    : (isAllOption && (!filterState[filterKey] || filterState[filterKey].length === 0));

                // Crear estructura de Checkbox Badge
                const container = document.createElement("label");
                container.className = `filter-checkbox-container ${isChecked && !isAllOption ? "selected" : ""}`;

                if (isAllOption) {
                    // La opción "Todos" actúa como botón limpiador de este filtro
                    container.innerHTML = `
                        <input type="radio" name="radio_${filterKey}" ${isChecked ? "checked" : ""}>
                        <span>${label}</span>
                    `;
                    const radio = container.querySelector("input");
                    radio.addEventListener("change", () => {
                        filterState[filterKey] = [];
                        changedState = true;
                        applyButton.classList.add("visible");
                        
                        // Actualizar UI visual del grupo
                        list.querySelectorAll(".filter-checkbox-container").forEach(c => c.classList.remove("selected"));
                    });
                } else {
                    container.innerHTML = `
                        <input type="checkbox" ${isChecked ? "checked" : ""}>
                        <span>${label}</span>
                    `;
                    const checkbox = container.querySelector("input");
                    checkbox.addEventListener("change", (e) => {
                        if (!filterState[filterKey]) {
                            filterState[filterKey] = [];
                        }

                        // Desmarcar opción "Todos" en caso de que esté marcada
                        const allRadio = list.querySelector(`input[type="radio"]`);
                        if (allRadio) allRadio.checked = false;

                        if (e.target.checked) {
                            if (!filterState[filterKey].includes(val)) {
                                filterState[filterKey].push(val);
                            }
                            container.classList.add("selected");
                        } else {
                            filterState[filterKey] = filterState[filterKey].filter(v => v !== val);
                            container.classList.remove("selected");
                            
                            // Si se desmarcaron todos, marcar "Todos" por defecto
                            if (filterState[filterKey].length === 0 && allRadio) {
                                allRadio.checked = true;
                            }
                        }

                        changedState = true;
                        applyButton.classList.add("visible");
                    });
                }

                // Reemplazar contenido de LI
                item.innerHTML = "";
                item.appendChild(container);
            });
        }
    });
});
