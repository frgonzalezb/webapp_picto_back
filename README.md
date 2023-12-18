# Proyecto Picto (backend)

Este es el repositorio privado para el backend de Picto, un Sistema Alternativo y Aumentativo de Comunicación (SAAC), desarrollado por Tecnologías Adaptativas Para la Inclusión (TAPI), parte del CITT del Duoc UC, sede San Andrés de Concepción.

## 🤝 Equipo:

**Jefe de proyecto y supervisor de práctica:**  
  
👨‍💼 Cristhian Beltrán Provoste  
(Fundador de TAPI, Co Fundador de ECOTECNO INCLUSIÓN, Co Fundador de Fundación INCLUSIVO, Ingeniero Automatización, Gestor de proyectos de innovación inclusivos, Docente en UBB y en Duoc Concepción)

**Practicantes desarrolladores, primera versión**:  
👨‍💻 Javier Fuenzalida  
👨‍💻 Javier Baeza
  
**Practicantes desarrolladores, segunda versión**:  
👨‍💻 Francisco González Bustamante (analista programador computacional) -> Frontend dev  
👨‍💻 Erwin Núñez (ingeniería en informática) -> Backend dev

## 🧠 ¿Qué es un SAAC?

Una descripción breve, en palabras del Proyecto ARASAAC[^1] (Centro Aragonés para la Comunicación Aumentativa y Alternativa):  
  
> Los Sistemas Aumentativos y Alternativos de Comunicación (SAAC) son **formas de expresión diferentes** del lenguaje hablado que tienen como objetivo **aumentar el nivel de expresión (aumentativo)** y/o **compensar (alternativo) las dificultades de comunicación** que presentan algunas personas en este área.
  
¿Por qué utilizar un SAAC?:
> La comunicación y el lenguaje son esenciales para todo ser humano, para relacionarse con los demás, para aprender, para disfrutar y para participar en la sociedad y hoy en día, gracias a estos sistemas, no deben verse frenados a causa de las dificultades en el lenguaje oral. Por esta razón, todas las personas, ya sean niños, jóvenes, adultos o ancianos, que por cualquier causa no han adquirido o han perdido un nivel de habla suficiente para comunicarse de forma satisfactoria, necesitan usar un SAAC.
  
¿Cuándo puede ser necesario utilizar un SAAC?:
  
> Entre las causas que pueden hacer necesario el uso de un SAAC encontramos la parálisis cerebral (PC), la discapacidad intelectual, los trastornos del espectro autista (TEA), las enfermedades neurológicas tales como la esclerosis lateral amiotrófica (ELA), la esclerosis múltiple (EM) o el párkinson, las distrofias musculares, los traumatismos cráneo-encefálicos, las afasias o las pluridiscapacidades de tipologías diversas, entre muchas otras.
  
¿Qué recursos se ocupan en un SAAC?:
  
> La Comunicación Aumentativa y Alternativa incluye diversos **sistemas de símbolos**, tanto gráficos (fotografías, dibujos, pictogramas, palabras o letras) como gestuales (mímica, gestos o signos manuales) y, en el caso de los primeros, requiere también el uso de **productos de apoyo**. Los diversos sistemas de símbolos se adaptan a las necesidades de personas con edades y habilidades motrices, cognitivas y lingüísticas muy dispares.

Para mayor información, puede acceder al artículo completo de ARASAAC sobre el tema [AQUÍ](https://arasaac.org/aac).

## 🔎 El software PICTO: logros, necesidades, problemas y nuestra solución

### 🏆 Logros de la primera versión
+ Software totalmente funcional (al momento de entrega).
+ Uso de herramientas novedosas como FastAPI (backend) y Vue.js (frontend).
+ Permite realizar CRUD completo y de fácil uso para los pictogramas, audios y rutinas.
+ Se incluyen barras de búsqueda para acceder fácilmente a los contenidos requeridos por el usuario.
+ El sistema se puede devolver a su versión inicial (factory reset) en caso de necesitarse.
+ Interfaz gráfica sencilla y responsiva, aprobada por el usuario final en la entrega final.

### 📝 Necesidades actuales declaradas por el jefe de proyectos para la nueva versión
+ Desplegar la aplicación en web, para un fácil acceso por los usuarios finales. Se desprende de esto:
  + Implementar separación de entornos para diferentes usuarios, con distintos roles, permisos y restricciones.
  + Proteger estrictamente la integridad y privacidad de los datos de los usuarios y del sistema.
  + Acordar un servicio de hosting que sea asequible y seguro para el despliegue del sistema.
  + Mantener o superar el buen nivel de experiencia de usuario (UX) alcanzado en la versión previa.
+ Documentar todos los procesos críticos, sean en informes o diagramas de ingeniería, o en el mismo código.

Adicionalmente, el jefe de proyectos ha considerado postular este software a un fondo concursable, lo que implica un futuro desarrollo en mejoras y correcciones, por lo que el factor de _escalabilidad_ es fundamental.

### ❌ Problemas detectados por el actual equipo de desarrollo
+ El software inicial sólo puede ser utilizado de forma viable en local. Por ejemplo:
  + No permite sesiones multiusuario, por lo que un cambio realizado por un usuario puede afectar el contenido creado por otro.
  + Todos los usuarios tienen virtualmente permisos de administrador: pueden realizar el CRUD completo de todos los recursos.
  + No hay trazabilidad de los cambios realizados (por ejemplo: qué usuario eliminó una rutina y cuándo).
+ Carencia absoluta de documentación, tanto de ingeniería como de código.
+ Uso de numerosas librerías actualmente deprecadas, especialmente en el frontend.

### ✔ Nuestra solución (v2)
Ofrecer una versión mejorada del software PICTO, basada en la primera versión, que mantenga los logros alcanzados, dé una solución viable a los problemas encontrados y que implemente satisfactoriamente las necesidades del cliente, para uso seguro y confiable de cualquier usuario interesado en la aplicación.

## ⚙ Especificaciones técnicas para la nueva versión del proyecto

### 🖥 Frontend:
- **Framework:** Vue.js 3.3.4
- **Lenguajes:** HTML, SCSS, TypeScript

### 🗃️ Backend:
- **Framework:** Django 4.2.3 | Django REST Framework 3.14.0
- **Lenguaje:** Python 3.11.4
- **Base de datos:** MySQL

### 🛠 Herramientas:
- **IDEs:** Visual Studio Code, Notepad++
- **Clientes API (testing):** Postman, Insomnia

## ⬇ Instalación

1. Clonar este repositorio en su entorno local.
2. Abrir una terminal y dirigirse al directorio del repositorio local.
3. Generar el entorno virtual mediante el siguiente comando:
```
python -m venv .venv
```
4. Instalar todas las librerías en su entorno virtual, desde el archivo `requirements.txt`, con el siguiente comando:
```
pip install -r requirements.txt
```

## ⚠ IMPORTANTE ⚠

1. **¡Siempre trabajar en ramas (branches), nunca directamente desde el `main`!** Hacer tantas ramas como sean necesarias.
2. Una vez que se ha logrado implementar exitosamente algo importante en una rama, crear `pull request` a `main` y comparar cuidadosamente el código entre ambas.  
  
👉 **¡Si hay conflictos, RESOLVERLOS TODOS antes de hacer el merge!** 👈  
  
Si no hay, o ya han sido los conflictos resueltos, puede realizar el merge al `main` con seguridad. ✅

## 🔖 Links de interés
  
* [Cuenta Instagram oficial de TAPI][tapi-ig]
* [Página del CITT][citt]
* [Repositorio frontend][frontend] (privado, requiere acceso autorizado)
* [Documentación de Vue.js][docu-vue]
* [Documentación de Django][docu-django]
* [Documentación de Django REST Framework][docu-drf]
* [Curso gratuito de Django REST Framework en español][curso-drf]
* [Postman][postman] (herramienta cliente API REST)
* [Insomnia][insomnia] (otra herramienta cliente API REST)
* [Curso gratuito de Postman en español][curso-postman]
* [Railway][railway] (herramienta de despliegue backend)
* [ARASAAC][arasaac] (ejemplo de un SAAC e inspiración de este proyecto)

[tapi-ig]: https://www.instagram.com/tapi_lab/
[citt]: https://www.duoc.cl/escuela/informatica-telecomunicaciones/citt/
[frontend]: https://github.com/frgonzalezb/picto_frontend
[docu-vue]: https://vuejs.org/guide/introduction.html
[docu-django]: https://www.djangoproject.com/
[docu-drf]: https://www.django-rest-framework.org/
[curso-drf]: https://www.youtube.com/playlist?list=PLMbRqrU_kvbRI4PgSzgbh8XPEwC1RNj8F
[postman]: https://www.postman.com/
[insomnia]: https://insomnia.rest/download
[curso-postman]: https://www.youtube.com/watch?v=NENmQYNfZxI
[railway]: https://railway.app/
[arasaac]: https://arasaac.org/index.html  
  
[^1]: ARASAAC (s/f). [¿Qué son los SAAC?](https://arasaac.org/aac)
