document.getElementById('submit-button').addEventListener('click', () => {
  const gameId = document.getElementById('game-select').value;
  const scoreDifference = document.getElementById('score-difference').value;
  const messageContent = document.getElementById('message-content').value;
  const scheduleTime = document.getElementById('schedule-time').value;

  if (!gameId || !scoreDifference || !messageContent || !scheduleTime) {
    // Handle missing input with user feedback
    return;
  }

  fetch('/api/schedule_message/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      game_id: gameId,
      score_difference: scoreDifference,
      message_content: messageContent,
      schedule_time: scheduleTime
    })
  })
  .then(response => response.json())
  .then(data => {
    // Handle successful scheduling response
  })
  .catch(error => {
    console.error('Error scheduling message:', error);
    // Handle failed scheduling attempt with user feedback
  });
});

