# Simulación de intersección semafórica basada en agentes

## 1. Introducción
La congestión en intersecciones urbanas surge cuando los sistemas de semáforos no se ajustan a variaciones dinámicas del tráfico. Los ciclos fijos, aunque simples de implementar, no responden a fluctuaciones en la demanda vehicular, especialmente en horas punta o situaciones irregulares. Esto incrementa los tiempos de espera, genera acumulación de vehículos y reduce la eficiencia del flujo.

Este proyecto presenta una simulación basada en agentes en la cual el agente principal es el semáforo. Se comparan dos enfoques: un semáforo de tipo Fixed con tiempos predefinidos y constantes, y un semáforo Adaptive que percibe el flujo vehicular y ajusta sus ciclos en función de la demanda observada.

El objetivo es evaluar el impacto de ambos enfoques en escenarios reales de tráfico, midiendo indicadores como tiempos promedio y capacidad de procesamiento de vehículos.

---

## 2. Marco Teórico

### 2.1 Sistemas basados en agentes

Un agente es una entidad autónoma capaz de percibir su entorno, tomar decisiones y ejecutar acciones con base en reglas o metas. En sistemas complejos como el tráfico, los modelos basados en agentes permiten describir comportamientos individuales y su efecto emergente en el sistema global.

Las características relevantes de este paradigma incluyen:
- Autonomía: los agentes operan sin control centralizado directo.
- Localidad: sus decisiones dependen de información disponible en su contexto inmediato.
- Emergencia: el flujo global surge de interacciones locales.

### 2.2 Agente semafórico

El semáforo opera como agente principal. Detecta condiciones del tráfico y decide cómo gestionar su ciclo. El agente puede encontrarse en estados discretos (verde, amarillo y rojo) y determina la transición entre ellos.

Se modelan dos comportamientos:

#### Semáforo Fixed
- Mantiene duraciones constantes para cada fase.
- No responde a condiciones del tráfico real.

#### Semáforo Adaptive
- Observa la cantidad de vehículos esperando por vía.
- Ajusta la duración de la fase verde en función del flujo vehicular.

---

## 3. Simulación

### 3.1 Entorno

El entorno consiste en una intersección de cuatro vías con flujo bidireccional. Los vehículos entran desde los extremos de cada vía, avanzan hasta el cruce y salen al finalizar el tramo. No poseen comportamiento inteligente: solo avanzan si el semáforo lo permite y se detienen cuando encuentran luz roja o congestión.

La simulación opera en pasos discretos. En cada paso:
- Se generan vehículos según las tasas del escenario.
- El semáforo evalúa el estado del tráfico.
- Los vehículos avanzan o detienen su movimiento según el estado del agente.

### 3.2 Escenarios

Se simularon tres condiciones urbanas representativas:

- Hora punta mañana
- Tráfico promedio
- Hora punta tarde

En cada escenario, la tasa de llegada vehicular varía y afecta directamente el número de vehículos en espera. Cada simulación cubre un día completo y se ejecuta repetidamente para observar consistencia en los resultados.

---

## 4. Implementación

- Lenguaje: Python.
- Tipo de modelo: simulación discreta basada en agentes.
- Generación de vehículos basada en tasas de llegada dependientes del escenario.
- El agente semafórico evalúa el estado del tráfico y aplica su política correspondiente.

Durante la ejecución, el sistema registra tiempos de tránsito, vehículos procesados y acumulación por vía para analizar la eficiencia de cada modelo de control.

---

## 5. Resultados

El modo Fixed tiende a producir mayores tiempos promedio cuando el tráfico supera su capacidad nominal, debido a su incapacidad para reaccionar a condiciones variables. El modo Adaptive reduce los tiempos promedio generales, especialmente en escenarios con alta demanda, al asignar más tiempo verde a las vías congestionadas.
La cantidad de vehículos procesados por día es similar entre ambos modos, pero el control adaptativo distribuye mejor el flujo y evita la formación prolongada de colas.

---
## 6. Conclusiones

La simulación muestra que un semáforo adaptativo mejora la circulación en comparación con un esquema fijo. El enfoque reactivo distribuye el tiempo de paso en función del tráfico real, lo que reduce los tiempos de espera y aumenta la fluidez.

Entre las limitaciones se encuentran:
- Los vehículos no poseen comportamiento autónomo.
- El modelo no considera peatones ni transporte público.
- No se contempla coordinación entre múltiples intersecciones.

Como trabajo futuro se plantea:
- Integración de aprendizaje por refuerzo.
- Coordinación entre agentes en múltiples intersecciones.
- Incorporación de prioridades dinámicas.

---

## 7. Declaración de uso de IA

Se utilizó ChatGPT para la asistencia en redacción y organización del documento. Prompts empleados para estructuración, síntesis y estandarización de contenido.


