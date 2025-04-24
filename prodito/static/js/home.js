document.addEventListener('DOMContentLoaded', function () {
  const Calendar = window.tui.Calendar

  const cal = new Calendar('#calendar', {
    defaultView: 'month',
    theme: {
      common: {
        backgroundColor: '--',
        borderColor: '#1c343f',
        color: '#ffffff'
      }
    },
    useDetailPopup: true,
    taskView: true,
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
})
