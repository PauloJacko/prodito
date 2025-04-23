;(() => {
  document.addEventListener('DOMContentLoaded', function () {
    const Calendar = window.tui.Calendar

    const cal = new Calendar('#calendar', {
      defaultView: 'month',
      calendars: [],
      useFormPopup: true,
      useDetailPopup: true,
      taskView: true,
      theme: {
        common: {
          backgroundColor: '--',
          borderColor: '#1c343f',
          color: '#ffffff'
        }
      }
    })

    document.getElementById('prevBtn').addEventListener('click', () => {
      cal.prev()
    })

    document.getElementById('todayBtn').addEventListener('click', () => {
      cal.today()
    })

    document.getElementById('nextBtn').addEventListener('click', () => {
      cal.next()
    })
  })
})()
