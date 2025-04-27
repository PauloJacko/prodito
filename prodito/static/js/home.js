document.addEventListener('DOMContentLoaded', function () {
  const Calendar = window.tui.Calendar
  const modal = document.getElementById('modalCrearTarea')
  const btnCancelar = document.getElementById('btnCancelar')

  btnCancelar.addEventListener('click', function () {
    modal.style.display = 'none'
    modal.close()
  })

  const cal = new Calendar('#calendar', {
    defaultView: 'month',
    theme: {
      common: {
        backgroundColor: '--',
        borderColor: '#1c343f',
        color: '#ffffff'
      }
    },
    calendars: [
      {
        id: 'local',
        name: 'Tareas',
        color: '#ffffff',
        bgColor: '#00a9ff',
        dragBgColor: '#00a9ff',
        borderColor: '#00a9ff'
      },
      {
        id: 'google',
        name: 'Google Calendar',
        color: '#ffffff',
        bgColor: '#03bd9e',
        dragBgColor: '#03bd9e',
        borderColor: '#03bd9e'
      }
    ]
  })

  document.getElementById('prevBtn').addEventListener('click', () => cal.prev())
  document
    .getElementById('todayBtn')
    .addEventListener('click', () => cal.today())
  document.getElementById('nextBtn').addEventListener('click', () => cal.next())

  fetch('/api/tareas/')
    .then((response) => response.json())
    .then((tareas) => {
      tareas.forEach((t) => (t.calendarId = 'local'))
      cal.createEvents(tareas)
    })
    .catch((error) => console.error('Error al cargar tareas:', error))

  fetch('/api/google-calendar/')
    .then((response) => response.json())
    .then((eventos) => {
      eventos.forEach((e) => (e.calendarId = 'google'))
      cal.createEvents(eventos)
    })
    .catch((error) =>
      console.error('Error al cargar eventos de Google Calendar:', error)
    )

  document
    .getElementById('formCrearTarea')
    .addEventListener('submit', function (e) {
      e.preventDefault()

      const titulo = document.getElementById('tituloInput').value
      const fecha = document.getElementById('fechaInput').value
      const descripcion = document.getElementById('descripcionInput').value

      const fechaFormateada = new Date(fecha).toISOString().split('T')[0]

      const nuevoEvento = {
        id: String(new Date().getTime()),
        calendarId: 'local',
        title: titulo,
        start: fechaFormateada,
        end: fechaFormateada,
        category: 'time'
      }
      cal.createEvents([nuevoEvento])

      fetch('/api/crear-tarea/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ titulo, fecha: fechaFormateada, descripcion })
      })
        .then((response) => {
          if (response.ok) {
            modal.style.display = 'none'
            cerrarModal()
          } else {
            alert('Error al guardar')
          }
        })
        .catch((error) => {
          console.error('Error al guardar la tarea:', error)
        })
    })

  cal.on('selectDateTime', function (event) {
    const fechaSeleccionada = event.start
    abrirModal(fechaSeleccionada)
  })

  function abrirModal(fecha) {
    const inputFecha = document.getElementById('fechaInput')

    inputFecha.value =
      fecha.toISOString().split('T')[0] +
      ' ' +
      fecha.toISOString().split('T')[1].slice(0, 5)

    modal.style.display = 'block'
    modal.showModal()
  }

  function cerrarModal() {
    modal.close()
  }

  flatpickr('#fechaInput', {
    enableTime: true,
    dateFormat: 'Y-m-d H:i',
    time_24hr: true,
    static: true,
    position: 'above'
  })
})
