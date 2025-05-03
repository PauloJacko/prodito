document.addEventListener('DOMContentLoaded', function () {
  const Calendar = window.tui.Calendar
  const modal = document.getElementById('modalCrearTarea')
  const btnCancelar = document.getElementById('btnCancelar')
  const monthSelector = document.getElementById('monthSelector')
  const yearSelector = document.getElementById('yearSelector')
  const btnNuevaTarea = document.getElementById('btnAbrirModal')

  btnCancelar.addEventListener('click', function () {
    modal.style.display = 'none'
    modal.close()
  })

  btnNuevaTarea.addEventListener('click', function () {
    const fechaInicio = new Date()
    const fechaFin = new Date()
    fechaFin.setHours(fechaFin.getHours() + 1)
    fechaFin.setSeconds(0, 0)
    fechaInicio.setSeconds(0, 0)
    pickerFechaInicio.setDate(fechaInicio)
    pickerHoraInicio.setDate(fechaInicio)
    pickerFechaFin.setDate(fechaFin)
    pickerHoraFin.setDate(fechaFin)
    modal.style.display = 'block'
    modal.showModal()
  })

  modal.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      event.preventDefault()
      event.stopPropagation()
      return false
    }
  })

  function formatTime(date) {
    const d = new Date(date)
    const hours = d.getHours().toString().padStart(2, '0')
    const minutes = d.getMinutes().toString().padStart(2, '0')
    return `${hours}:${minutes}`
  }

  const cal = new Calendar('#calendar', {
    defaultView: 'month',
    theme: {
      common: {
        backgroundColor: '--',
        borderColor: '#1c343f',
        color: '#ffffff'
      }
    },
    isReadOnly: false,
    template: {
      time(event) {
        const { start, end, title } = event

        return `<span>${formatTime(start)}~${formatTime(end)} ${title}</span>`
      },
      allday(event) {
        return `<span style="color: gray;">${event.title}</span>`
      }
    },
    calendars: [
      {
        id: 'local',
        name: 'Personal',
        backgroundColor: '#03bd9e'
      },
      {
        id: 'google',
        name: 'Work',
        backgroundColor: '#00a9ff'
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
      const descripcion = document.getElementById('descripcionInput').value

      const fecha = document.getElementById('fechaInicioInput').value
      const hora = document.getElementById('horaInicioInput').value
      const fecha_fin = document.getElementById('fechaFinInput').value
      const hora_fin = document.getElementById('horaFinInput').value

      const nuevoEvento = {
        id: String(new Date().getTime()),
        calendarId: 'local',
        title: titulo,
        start: `${fecha}T${hora}`,
        end: `${fecha_fin}T${hora_fin}`,
        category: 'time'
      }

      cal.createEvents([nuevoEvento])

      fetch('/api/crear-tarea/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          titulo,
          descripcion,
          fecha,
          hora,
          fecha_fin,
          hora_fin
        })
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
    const fechaInicio = event.start
    const fechaFin = event.end
    abrirModal(fechaInicio, fechaFin)
  })

  const pickerFechaInicio = flatpickr('#fechaInicioInput', {
    dateFormat: 'Y-m-d',
    static: true,
    position: 'above'
  })

  const pickerHoraInicio = flatpickr('#horaInicioInput', {
    enableTime: true,
    noCalendar: true,
    dateFormat: 'H:i',
    time_24hr: true,
    static: true,
    position: 'above',
    minuteIncrement: 1
  })

  const pickerFechaFin = flatpickr('#fechaFinInput', {
    dateFormat: 'Y-m-d',
    static: true,
    position: 'above'
  })

  const pickerHoraFin = flatpickr('#horaFinInput', {
    enableTime: true,
    noCalendar: true,
    dateFormat: 'H:i',
    time_24hr: true,
    static: true,
    minuteIncrement: 1,
    position: 'above'
  })

  function abrirModal(fechaInicio, fechaFin) {
    fechaInicio.setSeconds(0, 0)
    fechaFin.setSeconds(0, 0)

    pickerFechaInicio.setDate(fechaInicio)
    pickerHoraInicio.setDate(fechaInicio)
    pickerFechaFin.setDate(fechaFin)
    pickerHoraFin.setDate(fechaFin)

    modal.style.display = 'block'
    modal.showModal()
  }

  function cerrarModal() {
    const form = document.getElementById('formCrearTarea')

    modal.close()
    form.reset()

    if (pickerFechaInicio) pickerFechaInicio.clear()
    if (pickerHoraInicio) pickerHoraInicio.clear()
    if (pickerFechaFin) pickerFechaFin.clear()
    if (pickerHoraFin) pickerHoraFin.clear()
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
        cal.clear()
        cal.createEvents(eventos)
      })
      .catch((err) => {
        console.error('Error al obtener eventos:', err)
      })
  }

  cargarEventos()
})
