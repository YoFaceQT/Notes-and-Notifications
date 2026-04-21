import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function getErrorText(error) {
  const msg = error.response?.data?.detail;
  if (typeof msg === 'string') return msg;
  if (Array.isArray(msg)) return msg.map((item) => item?.msg ?? item).join(', ');
  return 'Ошибка запроса';
}

// Компонент для отображения одной задачи с таймером
function TaskItem({ task, onEdit, onDelete }) {
  const [timeLeft, setTimeLeft] = useState(null);
  const [isExpired, setIsExpired] = useState(false);

useEffect(() => {
  if (!task.reminder_at || task.status !== 'IN_PROGRESS') {
    setTimeLeft(null);
    setIsExpired(false);
    return;
  }

  // Нормализуем строку: заменяем пробел на T, добавляем Z если нет часового пояса
  let dateStr = task.reminder_at.replace(' ', 'T');
  if (!dateStr.endsWith('Z') && !dateStr.includes('+') && !dateStr.includes('-')) {
    dateStr += 'Z';
  }
  const deadline = new Date(dateStr);

  if (isNaN(deadline.getTime())) {
    console.error('Invalid date:', task.reminder_at);
    setTimeLeft(null);
    setIsExpired(false);
    return;
  }

  const updateTimer = () => {
    const now = new Date();
    const diff = deadline - now;
    if (diff <= 0) {
      setTimeLeft(null);
      setIsExpired(true);
      return;
    }
    setIsExpired(false);
    const totalSeconds = Math.floor(diff / 1000);
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    const formatted = hours > 0
      ? `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
      : `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    setTimeLeft(formatted);
  };

  updateTimer();
  const interval = setInterval(updateTimer, 1000);
  return () => clearInterval(interval);
}, [task.reminder_at, task.status]);
  // Определяем текст статуса
  let statusText = '';
if (task.status === 'IN_PROGRESS') {
    statusText = '⏳ В работе';
} else if (task.status === 'FAILED_TO_SEND') {
    statusText = '❌ Ошибка отправки';
} else if (task.status === 'SUCCESSFULLY_SENT') {
    statusText = '✅ Сообщение успешно отправлено';
} else {
    statusText = '⏲️ Нет таймера';
}

  return (
    <li>
      <div className="task-content">
        <span className="task-title">{task.name}</span>
        {task.description && (
          <span className="task-description">{task.description}</span>
        )}
        <span className="task-state">{statusText}</span>
        {!isExpired && timeLeft && (
          <div className="task-timer">🕒 Осталось: {timeLeft}</div>
        )}
        {isExpired && (
          <div className="task-timer expired">⏰ Время вышло</div>
        )}
      </div>
      <div className="task-actions">
        <button className="btn" onClick={() => onEdit(task)}>Изменить</button>
        <button className="btn btn-danger" onClick={() => onDelete(task.id)}>Удалить</button>
      </div>
    </li>
  );
}

function App() {
  const [taskName, setTaskName] = useState('');
  const [taskDescription, setTaskDescription] = useState('');
  const [taskRemindMinutes, setTaskRemindMinutes] = useState('');
  const [tasks, setTasks] = useState([]);
  const [editingTaskId, setEditingTaskId] = useState(null);
  const [editingTaskOriginal, setEditingTaskOriginal] = useState(null);
  const [statusMessage, setStatusMessage] = useState('');

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/tasks`);
      setTasks(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Error fetching tasks:', error);
      setStatusMessage('Ошибка при загрузке задач');
    }
  };

  const resetForm = () => {
    setTaskName('');
    setTaskDescription('');
    setTaskRemindMinutes('');
    setEditingTaskId(null);
    setEditingTaskOriginal(null);
  };

  const handleSubmit = async () => {
    const name = taskName.trim();
    if (!name) return;

    // Преобразуем минуты в число или null
    let remindAfterMinutes = null;
    if (taskRemindMinutes !== '') {
      const parsed = parseInt(taskRemindMinutes, 10);
      if (!isNaN(parsed) && parsed > 0) {
        remindAfterMinutes = parsed;
      }
    }

    try {
      if (editingTaskId) {
        const patchData = {};
        if (!editingTaskOriginal || name !== editingTaskOriginal.name) {
          patchData.name = name;
        }
        if (!editingTaskOriginal || taskDescription !== editingTaskOriginal.description) {
          patchData.description = taskDescription || null;
        }
        if (!editingTaskOriginal || remindAfterMinutes !== editingTaskOriginal.remind_after_minutes) {
          patchData.remind_after_minutes = remindAfterMinutes;
        }
        if (Object.keys(patchData).length === 0) {
          setStatusMessage('Изменений нет');
          return;
        }
        await axios.patch(`${API_BASE_URL}/tasks/${editingTaskId}`, patchData);
        setStatusMessage('Задача обновлена');
      } else {
        await axios.post(`${API_BASE_URL}/tasks`, {
          name,
          description: taskDescription || null,
          remind_after_minutes: remindAfterMinutes,
        });
        setStatusMessage('Задача создана');
      }
      resetForm();
      fetchTasks();
    } catch (error) {
      console.error('Error submitting task:', error);
      setStatusMessage(`Ошибка: ${getErrorText(error)}`);
    }
  };

  const handleEdit = (task) => {
    setTaskName(task.name);
    setTaskDescription(task.description || '');
    setTaskRemindMinutes(task.remind_after_minutes?.toString() || '');
    setEditingTaskId(task.id);
    setEditingTaskOriginal({
      name: task.name,
      description: task.description,
      remind_after_minutes: task.remind_after_minutes,
    });
    setStatusMessage('');
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`${API_BASE_URL}/tasks/${id}`);
      if (editingTaskId === id) resetForm();
      fetchTasks();
    } catch (error) {
      console.error('Error deleting task:', error);
      setStatusMessage(`Ошибка: ${getErrorText(error)}`);
    }
  };

  return (
    <div className="app-shell">
      <main className="App">
        <section className="panel editor-panel">
          <div className="input-row">
            <input
              type="text"
              value={taskName}
              onChange={(e) => setTaskName(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
              placeholder="Название задачи"
            />
            <input
              type="text"
              value={taskDescription}
              onChange={(e) => setTaskDescription(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
              placeholder="Описание (необязательно)"
            />
            <input
              type="number"
              min="0"
              value={taskRemindMinutes}
              onChange={(e) => setTaskRemindMinutes(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
              placeholder="Таймер (минуты)"
              className="timer-input"
            />
            <button className="btn btn-primary" onClick={handleSubmit}>
              {editingTaskId ? 'Сохранить' : 'Добавить'}
            </button>
          </div>
          <div className="action-row">
            <button className="btn" onClick={resetForm}>
              {editingTaskId ? 'Отменить редактирование' : 'Очистить поля'}
            </button>
          </div>
          {statusMessage && <div className="status-message">{statusMessage}</div>}
        </section>

        <section className="panel tasks-panel">
          <div className="tasks-toolbar">
            <div className="stats">
              <span className="stat-pill">Всего: {tasks.length}</span>
            </div>
            <button className="btn" onClick={fetchTasks}>Обновить</button>
          </div>
          {tasks.length === 0 ? (
            <div className="empty-state">Пока пусто. Добавьте первую задачу выше.</div>
          ) : (
            <ul>
              {tasks.map((task) => (
                <TaskItem
                  key={task.id}
                  task={task}
                  onEdit={handleEdit}
                  onDelete={handleDelete}
                />
              ))}
            </ul>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;