document.addEventListener('DOMContentLoaded', function () {
  const Calendar = window.tui.Calendar
  const modal = document.getElementById('modalCrearTarea')
  const btnCancelar = document.getElementById('btnCancelar')
  const monthSelector = document.getElementById('monthSelector')
  const yearSelector = document.getElementById('yearSelector')
  btnCancelar.addEventListener('click', function () {
    modal.style.display = 'none'
    modal.close()
  })

  modal.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      event.preventDefault()
      event.stopPropagation()
      return false
    }
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

  const currentYear = new Date().getFullYear()

  for (let year = currentYear - 5; year <= currentYear + 5; year++) {
    const option = document.createElement('option')
    option.value = year
    option.textContent = year
    if (year === currentYear) {
      option.selected = true
    }
    yearSelector.appendChild(option)
  }

  function updateSelectors() {
    const date = cal.getDate()
    monthSelector.value = date.getMonth()
    yearSelector.value = date.getFullYear()
  }

  function updateCalendarDate() {
    const month = parseInt(monthSelector.value)
    const year = parseInt(yearSelector.value)

    const newDate = new Date(year, month, 1)

    cal.setDate(newDate)
    updateSelectors()
  }

  monthSelector.addEventListener('change', () => {
    updateCalendarDate()
    cargarEventos()
  })
  yearSelector.addEventListener('change', () => {
    updateCalendarDate()
    cargarEventos()
  })

  cal.on('beforeCreateSchedule', updateSelectors)
  cal.on('clickDayname', updateSelectors)
  cal.on('clickSchedule', updateSelectors)
  cal.on('clickTimezonesCollapseBtn', updateSelectors)

  document.getElementById('viewSwitch').addEventListener('change', function () {
    const viewSwitchLabel = document.querySelector('label[for="viewSwitch"]')

    if (this.checked) {
      cal.changeView('week')
      viewSwitchLabel.textContent = 'Vista Semanal'
    } else {
      cal.changeView('month')
      viewSwitchLabel.textContent = 'Vista Mensual'
    }

    updateSelectors()
  })

  document.getElementById('prevBtn').addEventListener('click', function () {
    cal.prev()
    updateSelectors()
  })

  document.getElementById('todayBtn').addEventListener('click', function () {
    cal.today()
    updateSelectors()
  })

  document.getElementById('nextBtn').addEventListener('click', function () {
    cal.next()
    updateSelectors()
  })

  updateSelectors()

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
        start: fecha,
        end: fechaFormateada,
        category: 'time'
      }

      console.log({ fecha })
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

  const picker = flatpickr('#fechaInput', {
    enableTime: true,
    dateFormat: 'Y-m-d H:i',
    time_24hr: true,
    static: true,
    position: 'above'
  })

  function abrirModal(fecha) {
    fecha.setHours(12, 0, 0, 0)

    picker.setDate(fecha)

    modal.style.display = 'block'
    modal.showModal()
  }

  function cerrarModal() {
    modal.close()
  }

  fetch('/api/tareas/')
    .then((response) => response.json())
    .then((tareas) => {
      console.log({ tareas })
      tareas.forEach((t) => (t.calendarId = 'local'))
      cal.createEvents(tareas)
    })
    .catch((error) => console.error('Error al cargar tareas:', error))

  const cargarEventos = () => {
    const anio = parseInt(yearSelector.value)
    const mes = parseInt(monthSelector.value) + 1

    fetch(`/api/google-calendar/${anio}/${mes}/`)
      .then((res) => {
        if (!res.ok) throw new Error('Error al cargar eventos')
        return res.json()
      })
      .then((eventos) => {
        cal.createEvents(eventos)
      })
      .catch((err) => {
        console.error('Error al obtener eventos:', err)
      })
  }

  cargarEventos()
})
