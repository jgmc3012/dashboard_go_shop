select = document.getElementById('select_state_order')
select.addEventListener('change', (event) => {
    options = event.target.options
    i = event.target.selectedIndex
    valueOption = options[i].value
    window.location.search = `?state=${valueOption}`
})