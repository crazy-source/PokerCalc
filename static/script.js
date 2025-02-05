document.addEventListener('DOMContentLoaded', () => {
    // Function to handle login form submission
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    // Function to handle registration form submission
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }

    // Function to handle game creation form submission
    const createGameForm = document.getElementById('create-game-form');
    if (createGameForm) {
        createGameForm.addEventListener('submit', handleCreateGame);
    }

    // Function to handle adding a player to the game
    const addPlayerForm = document.getElementById('add-player-form');
    if (addPlayerForm) {
        addPlayerForm.addEventListener('submit', handleAddPlayer);
    }

    // Function to handle updating player buy-ins
    const updateBuyInsForm = document.getElementById('update-buy-ins-form');
    if (updateBuyInsForm) {
        updateBuyInsForm.addEventListener('submit', handleUpdateBuyIns);
    }

    // Function to handle updating player final chips
    const updateFinalChipsForm = document.getElementById('update-final-chips-form');
    if (updateFinalChipsForm) {
        updateFinalChipsForm.addEventListener('submit', handleUpdateFinalChips);
    }

    // Function to handle results calculation
    const calculateResultsBtn = document.getElementById('calculate-results-btn');
    if (calculateResultsBtn) {
        calculateResultsBtn.addEventListener('click', handleCalculateResults);
    }

    // Event listener for Casino Man type selection
    const casinoManTypeSelect = document.getElementById('casino-man-type');
    const selectCasinoManDiv = document.getElementById('select-casino-man');
    if (casinoManTypeSelect) {
        casinoManTypeSelect.addEventListener('change', function() {
            if (this.value === 'select') {
                selectCasinoManDiv.style.display = 'block';
                // Populate the select dropdown with users
                fetchUsersAndPopulateDropdown('selected-casino-man');
            } else {
                selectCasinoManDiv.style.display = 'none';
            }
        });
    }
});

async function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const messageDiv = document.getElementById('login-message');

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();

        if (response.ok) {
            messageDiv.textContent = data.message;
            // Redirect to game page or update UI as needed
            window.location.href = '/game'; // Redirect to the game page
        } else {
            messageDiv.textContent = data.message;
        }
    } catch (error) {
        console.error('Login error:', error);
        messageDiv.textContent = 'An error occurred during login.';
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const messageDiv = document.getElementById('register-message');

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();

        if (response.ok) {
            messageDiv.textContent = data.message;
            // Optionally redirect to login page or update UI
        } else {
            messageDiv.textContent = data.message;
        }
    } catch (error) {
        console.error('Registration error:', error);
        messageDiv.textContent = 'An error occurred during registration.';
    }
}

async function handleCreateGame(event) {
    event.preventDefault();
    const gameName = document.getElementById('game-name').value;
    const chipToMoneyRatio = parseFloat(document.getElementById('chip-to-money').value);
    const casinoManType = document.getElementById('casino-man-type').value;
    const selectedCasinoManId = casinoManType === 'select' ? parseInt(document.getElementById('selected-casino-man').value) : null;

    try {
        const response = await fetch('/create_game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ game_name: gameName, chip_to_money_ratio: chipToMoneyRatio, casino_man_type: casinoManType, selected_casino_man_id: selectedCasinoManId })
        });
        const data = await response.json();

        if (response.ok) {
            alert(data.message);
            // Further actions like updating UI, showing game ID, etc.
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error creating game:', error);
        alert('An error occurred while creating the game.');
    }
}

async function handleAddPlayer(event) {
    event.preventDefault();
    const userId = parseInt(document.getElementById('player-to-add').value);
    // Assume you have a way to get the current game ID, e.g., stored in a hidden field or a global variable
    const gameId = getCurrentGameId(); // Implement this function based on your app logic

    try {
        const response = await fetch('/add_player', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ game_id: gameId, user_id: userId })
        });
        const data = await response.json();

        if (response.ok) {
            alert(data.message);
            // Update UI to reflect the new player
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error adding player:', error);
        alert('An error occurred while adding the player.');
    }
}
// ... (previous functions: handleLogin, handleRegister, handleCreateGame, handleAddPlayer)

async function handleUpdateBuyIns(event) {
    event.preventDefault();
    const playerId = parseInt(document.getElementById('player-select').value);
    const buyIns = parseInt(document.getElementById('buy-ins').value);
    const gameId = getCurrentGameId(); // Get the current game ID

    try {
        const response = await fetch('/update_buy_ins', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ game_id: gameId, player_id: playerId, buy_ins: buyIns })
        });
        const data = await response.json();

        if (response.ok) {
            alert(data.message);
            // Optionally refresh the player list or update the UI
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error updating buy-ins:', error);
        alert('An error occurred while updating buy-ins.');
    }
}

async function handleUpdateFinalChips(event) {
    event.preventDefault();
    const playerId = parseInt(document.getElementById('player-select').value);
    const finalChips = parseInt(document.getElementById('final-chips').value);
    const gameId = getCurrentGameId(); // Get the current game ID

    try {
        const response = await fetch('/update_final_chips', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ game_id: gameId, player_id: playerId, final_chips: finalChips })
        });
        const data = await response.json();

        if (response.ok) {
            alert(data.message);
            // Optionally refresh the player list or update the UI
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error updating final chips:', error);
        alert('An error occurred while updating final chips.');
    }
}

async function handleCalculateResults(event) {
    event.preventDefault();
    const gameId = getCurrentGameId();

    try {
        const response = await fetch('/calculate_results', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ game_id: gameId })
        });
        const data = await response.json();

        if (response.ok) {
            displayResults(data.results);
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error calculating results:', error);
        alert('An error occurred while calculating results.');
    }
}

// Helper function to display results in the table
function displayResults(results) {
    const resultsTableBody = document.getElementById('results-table-body');
    resultsTableBody.innerHTML = ''; // Clear existing results

    results.forEach(player => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${player.username}</td>
            <td>${player.buy_ins}</td>
            <td>${player.final_chips}</td>
            <td>${player.amount}</td>
        `;
        resultsTableBody.appendChild(row);
    });

    document.getElementById('results-display').style.display = 'block'; // Show results
}

// Helper function to get the current game ID (you might need to adjust this)
function getCurrentGameId() {
    // Example: Get game ID from a hidden field or a global variable
    // return parseInt(document.getElementById('game-id').value); 
    // Or, if you are storing it in a global variable:
    // return currentGameId; 
    // For demonstration, let's assume it's a global variable set after game creation
    return window.currentGameId; // Ensure this is set correctly when a game is created
}

// Helper function to fetch users and populate a dropdown
async function fetchUsersAndPopulateDropdown(dropdownId) {
    try {
        const response = await fetch('/suggest_players');
        const users = await response.json();

        if (response.ok) {
            const dropdown = document.getElementById(dropdownId);
            dropdown.innerHTML = ''; // Clear existing options
            users.forEach(user => {
                const option = document.createElement('option');
                option.value = user.id;
                option.textContent = user.username;
                dropdown.appendChild(option);
            });
        } else {
            console.error('Failed to fetch users:', users.message);
        }
    } catch (error) {
        console.error('Error fetching users:', error);
    }
}

async function fetchPlayersAndPopulateDropdown(gameId, dropdownId) {
    try {
        const response = await fetch(`/game_players/${gameId}`);
        const players = await response.json();

        if (response.ok) {
            const dropdown = document.getElementById(dropdownId);
            dropdown.innerHTML = ''; // Clear existing options
            players.forEach(player => {
                const option = document.createElement('option');
                option.value = player.id;
                option.textContent = player.username;
                dropdown.appendChild(option);
            });
        } else {
            console.error('Failed to fetch players:', players.message);
        }
    } catch (error) {
        console.error('Error fetching players:', error);
    }
}