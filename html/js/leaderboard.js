const leaderboardBody = document.getElementById('leaderboardBody');
const spinner = document.getElementById('spinner');

async function fetchLeaderboard() {
    spinner.style.display = 'block';
    
    try {
        const response = await fetch('/api/leaderboard');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Clear existing content
        leaderboardBody.innerHTML = '';
        
        if (data.leaderboard && data.leaderboard.length > 0) {
            data.leaderboard.forEach((user, index) => {
                const row = document.createElement('tr');
                
                // Add special styling for top 3 users
                if (index < 3) {
                    row.classList.add('top-user');
                }
                
                row.innerHTML = `
                    <td><span class="rank-badge">${index + 1}</span></td>
                    <td>${user.username}</td>
                    <td>${user.redeem_count}</td>
                `;
                
                leaderboardBody.appendChild(row);
            });
        } else {
            // Show message if no data available
            const row = document.createElement('tr');
            row.innerHTML = `
                <td colspan="3" style="text-align: center; padding: 2rem; color: #666;">
                    No leaderboard data available yet
                </td>
            `;
            leaderboardBody.appendChild(row);
        }
    } catch (error) {
        console.error('Failed to fetch leaderboard:', error);
        
        // Show error message
        leaderboardBody.innerHTML = `
            <tr>
                <td colspan="3" style="text-align: center; padding: 2rem; color: #d32f2f;">
                    Error loading leaderboard. Please try again later.
                </td>
            </tr>
        `;
    } finally {
        spinner.style.display = 'none';
    }
}

// Initialize the leaderboard when page loads
document.addEventListener('DOMContentLoaded', function() {
    fetchLeaderboard();
});

// Refresh leaderboard every 30 seconds
setInterval(fetchLeaderboard, 30000);