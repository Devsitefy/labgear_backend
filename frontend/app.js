const API = '/api';
const state = {
  token: localStorage.getItem('labgear_token'),
  user: null,
  page: 'dashboard',
  equipment: [],
  reservations: [],
  maintenance: [],
  users: [],
  summary: null,
  categories: [],
  search: '',
  category: 'all',
  authMode: 'login',
  modal: null,
};

const pageTitles = {
  dashboard: 'Обзор',
  equipment: 'Оборудование',
  reservations: 'Бронирования',
  maintenance: 'Техническое обслуживание',
  reports: 'Отчётность',
  users: 'Пользователи',
};

const statusLabels = {
  available: 'Доступно', issued: 'Выдано', maintenance: 'На обслуживании', retired: 'Списано',
  pending: 'Ожидает решения', approved: 'Подтверждено', rejected: 'Отклонено',
  returned: 'Возвращено', cancelled: 'Отменено', open: 'Открыта', in_progress: 'В работе', resolved: 'Закрыта',
};
const roleLabels = { student: 'Студент', technician: 'Техник', admin: 'Администратор' };

function esc(value = '') {
  return String(value).replace(/[&<>"']/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[char]));
}

function equipmentIcon(category = '') {
  const value = category.toLowerCase();
  if (value.includes('измер')) return '📟';
  if (value.includes('генератор')) return '〰️';
  if (value.includes('питан')) return '🔋';
  if (value.includes('оптичес')) return '🔬';
  if (value.includes('паяль')) return '♨️';
  if (value.includes('производ')) return '🖨️';
  if (value.includes('диагност')) return '🌡️';
  if (value.includes('скан')) return '🧊';
  return '🧰';
}

function dateTime(value) {
  if (!value) return '—';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? '—' : date.toLocaleString('ru-RU', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
}

function dateOnly(value) {
  if (!value) return '—';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? '—' : date.toLocaleDateString('ru-RU', { day: '2-digit', month: 'long', year: 'numeric' });
}

function localDateTimeInput(date) {
  const offset = date.getTimezoneOffset();
  const local = new Date(date.getTime() - offset * 60000);
  return local.toISOString().slice(0, 16);
}

function toast(message, type = 'success') {
  const root = document.getElementById('toast-root');
  const node = document.createElement('div');
  node.className = `toast ${type === 'error' ? 'error' : ''}`;
  node.textContent = message;
  root.appendChild(node);
  setTimeout(() => node.remove(), 3600);
}

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;
  if (options.body && !headers['Content-Type']) headers['Content-Type'] = 'application/json';
  const response = await fetch(`${API}${path}`, { ...options, headers });
  if (response.status === 204) return null;
  const raw = await response.text();
  let data = null;
  try { data = raw ? JSON.parse(raw) : null; } catch { data = raw; }
  if (!response.ok) {
    const detail = data && typeof data === 'object' ? data.detail : null;
    throw new Error(Array.isArray(detail) ? detail.map((item) => item.msg).join(', ') : (detail || `Ошибка HTTP ${response.status}`));
  }
  return data;
}

function setToken(token) {
  state.token = token;
  if (token) localStorage.setItem('labgear_token', token);
  else localStorage.removeItem('labgear_token');
}

function showAuth() {
  const isRegister = state.authMode === 'register';
  document.getElementById('app').innerHTML = `
    <div class="auth-page">
      <section class="auth-visual">
        <div class="auth-brand"><div class="brand-mark">L</div><span>LabGear</span></div>
        <div class="auth-hero">
          <div class="eyebrow">Цифровая лаборатория</div>
          <h1>Оборудование.<br>Порядок.<br>Возможности.</h1>
          <p>Единое пространство для бронирования лабораторного оборудования, контроля выдачи и возврата, а также учёта технического состояния.</p>
        </div>
        <div class="visual-pills"><span>Умное бронирование</span><span>Контроль доступа</span><span>История операций</span></div>
      </section>
      <section class="auth-panel">
        <div class="auth-card">
          <div class="eyebrow" style="color:#6e8df0">LABGEAR / WORKSPACE</div>
          <h2>${isRegister ? 'Создать аккаунт' : 'С возвращением'}</h2>
          <p class="sub">${isRegister ? 'Зарегистрируйтесь, чтобы бронировать оборудование.' : 'Войдите в систему управления лабораторией.'}</p>
          <form id="auth-form">
            <div class="field"><label for="auth-email">Электронная почта</label><input id="auth-email" name="email" type="email" placeholder="name@university.ru" required autocomplete="username"></div>
            <div class="field"><label for="auth-password">Пароль</label><input id="auth-password" name="password" type="password" placeholder="Не менее 8 символов" required minlength="${isRegister ? 8 : 1}" autocomplete="${isRegister ? 'new-password' : 'current-password'}"></div>
            <button class="btn btn-primary btn-block" type="submit">${isRegister ? 'Зарегистрироваться' : 'Войти в систему'} <span>→</span></button>
          </form>
          ${isRegister ? '' : `
            <div class="demo-box">
              <div class="demo-title">ДЕМО-ДОСТУП · НАЖМИТЕ ДЛЯ АВТОЗАПОЛНЕНИЯ</div>
              <div class="demo-buttons">
                <button type="button" data-demo="admin">Администратор</button>
                <button type="button" data-demo="technician">Техник</button>
                <button type="button" data-demo="student">Студент</button>
              </div>
              <div class="demo-hint">Данные для входа также указаны в README проекта.</div>
            </div>`}
          <div class="auth-switch">${isRegister ? 'Уже есть аккаунт?' : 'Впервые в системе?'} <button class="text-button" type="button" data-action="toggle-auth">${isRegister ? 'Войти' : 'Создать аккаунт'}</button></div>
        </div>
      </section>
    </div>`;
}

function navItem(page, icon, label) {
  return `<button class="nav-item ${state.page === page ? 'active' : ''}" data-page="${page}"><span class="nav-icon">${icon}</span>${label}</button>`;
}

function showShell() {
  const initials = (state.user?.email || 'U').slice(0, 1).toUpperCase();
  const isStaff = ['admin', 'technician'].includes(state.user?.role);
  document.getElementById('app').innerHTML = `
    <div class="app-shell">
      <aside class="sidebar" id="sidebar">
        <div class="sidebar-brand"><div class="brand-mark">L</div><span>LabGear</span></div>
        <div class="nav-label">Рабочее пространство</div>
        <nav class="nav-list">
          ${navItem('dashboard', '⌂', 'Обзор')}
          ${navItem('equipment', '▦', 'Каталог оборудования')}
          ${navItem('reservations', '▤', isStaff ? 'Все бронирования' : 'Мои бронирования')}
          ${navItem('maintenance', '⚙', isStaff ? 'Обслуживание' : 'Неисправности')}
          ${isStaff ? navItem('reports', '▥', 'Отчётность') : ''}
          ${state.user?.role === 'admin' ? navItem('users', '♙', 'Пользователи') : ''}
        </nav>
        <div class="sidebar-bottom">
          <div class="user-chip"><div class="avatar">${initials}</div><div><strong>${esc(state.user?.email)}</strong><small>${roleLabels[state.user?.role] || state.user?.role}</small></div></div>
          <button class="logout-btn" data-action="logout">↪ &nbsp; Выйти из аккаунта</button>
        </div>
      </aside>
      <main class="main-area">
        <header class="topbar">
          <button class="mobile-menu" data-action="toggle-menu">☰</button>
          <div class="breadcrumb">LabGear <span style="color:#c1c9d6"> / </span> ${pageTitles[state.page] || 'Обзор'}</div>
          <div class="topbar-right"><span class="live-dot">Система активна</span><div class="top-avatar">${initials}</div></div>
        </header>
        <section class="content" id="page-content"><div class="empty-state">Загружаем данные…</div></section>
      </main>
    </div>`;
  loadPage().catch((error) => toast(error.message, 'error'));
}

async function refreshSharedData() {
  state.equipment = await api('/equipment?limit=200');
}

async function loadPage() {
  const content = document.getElementById('page-content');
  if (!content) return;
  await refreshSharedData();
  if (state.page === 'dashboard') {
    if (['admin', 'technician'].includes(state.user.role)) {
      const [summary, reservations, maintenance] = await Promise.all([
        api('/reports/summary'), api('/reservations'), api('/maintenance')
      ]);
      state.summary = summary;
      state.reservations = reservations;
      state.maintenance = maintenance;
    } else {
      const [reservations, maintenance] = await Promise.all([api('/reservations/me'), api('/maintenance/me')]);
      state.reservations = reservations;
      state.maintenance = maintenance;
    }
    renderDashboard();
  } else if (state.page === 'equipment') {
    renderEquipment();
  } else if (state.page === 'reservations') {
    state.reservations = await api(['admin', 'technician'].includes(state.user.role) ? '/reservations' : '/reservations/me');
    renderReservations();
  } else if (state.page === 'maintenance') {
    state.maintenance = await api(['admin', 'technician'].includes(state.user.role) ? '/maintenance' : '/maintenance/me');
    renderMaintenance();
  } else if (state.page === 'reports') {
    if (!['admin', 'technician'].includes(state.user.role)) return navigate('dashboard');
    const [summary, categories] = await Promise.all([api('/reports/summary'), api('/reports/by-category')]);
    state.summary = summary;
    state.categories = categories;
    renderReports();
  } else if (state.page === 'users') {
    if (state.user.role !== 'admin') return navigate('dashboard');
    state.users = await api('/users');
    renderUsers();
  }
}

function heading(title, subtitle, actions = '') {
  return `<div class="page-heading"><div><h1>${title}</h1><p>${subtitle}</p></div><div class="heading-actions">${actions}</div></div>`;
}

function statCard(label, value, icon, note = '') {
  return `<div class="stat-card"><div class="stat-top"><span>${label}</span><span class="stat-icon">${icon}</span></div><div class="stat-value">${value}</div><div class="stat-note">${note}</div></div>`;
}

function badge(status) {
  return `<span class="badge ${esc(status)}">${statusLabels[status] || esc(status)}</span>`;
}

function renderDashboard() {
  const content = document.getElementById('page-content');
  const isStaff = ['admin', 'technician'].includes(state.user.role);
  const available = state.equipment.filter((item) => item.status === 'available').length;
  const recentEquipment = state.equipment.slice(0, 4);
  const recentReservations = state.reservations.slice(0, 5);
  let stats;
  if (isStaff) {
    const s = state.summary || {};
    stats = [
      statCard('Всего единиц оборудования', s.equipment_total ?? 0, '▦', 'В каталоге лаборатории'),
      statCard('Доступно сейчас', s.available ?? available, '✓', 'Можно забронировать'),
      statCard('Активные бронирования', s.active_reservations ?? 0, '▤', 'Ожидают или находятся в работе'),
      statCard('Открытые неисправности', s.open_maintenance ?? 0, '⚙', 'Требуют внимания'),
    ].join('');
  } else {
    stats = [
      statCard('Доступно оборудования', available, '▦', 'В каталоге лаборатории'),
      statCard('Мои бронирования', state.reservations.length, '▤', 'За всё время'),
      statCard('Ожидают решения', state.reservations.filter((x) => x.status === 'pending').length, '◷', 'Заявки на согласовании'),
      statCard('Мои обращения', state.maintenance.length, '⚙', 'Сообщения о неисправностях'),
    ].join('');
  }
  content.innerHTML = `${heading(`Здравствуйте, ${esc(state.user.email.split('@')[0])}!`, 'Краткая сводка по лабораторному оборудованию и вашим действиям.', `<button class="btn btn-primary" data-page="equipment">＋ Забронировать оборудование</button>`)}
    <div class="stats-grid">${stats}</div>
    <div class="dashboard-grid">
      <section class="panel">
        <div class="panel-head"><div><h3>${isStaff ? 'Последние бронирования' : 'Мои последние бронирования'}</h3><p>Актуальные заявки и их статусы</p></div><button class="btn btn-outline btn-small" data-page="reservations">Все заявки →</button></div>
        <div class="panel-body">${recentReservations.length ? `<div class="quick-list">${recentReservations.map((r) => {
          const eq = state.equipment.find((e) => e.id === r.equipment_id);
          return `<div class="quick-item"><div class="equip-icon">${equipmentIcon(eq?.category)}</div><div class="quick-copy"><strong>${esc(eq?.name || `Оборудование #${r.equipment_id}`)}</strong><small>${dateTime(r.starts_at)} · ${isStaff ? `Пользователь #${r.user_id}` : 'Моя заявка'}</small></div>${badge(r.status)}</div>`;
        }).join('')}</div>` : `<div class="empty-state"><div class="empty-icon">▤</div><strong>Заявок пока нет</strong><span>Выберите оборудование в каталоге, чтобы создать первое бронирование.</span></div>`}</div>
      </section>
      <section class="panel">
        <div class="panel-head"><div><h3>Оборудование в каталоге</h3><p>Быстрый переход к доступным позициям</p></div><button class="btn btn-outline btn-small" data-page="equipment">Каталог →</button></div>
        <div class="panel-body"><div class="quick-list">${recentEquipment.map((item) => `<div class="quick-item"><div class="equip-icon">${equipmentIcon(item.category)}</div><div class="quick-copy"><strong>${esc(item.name)}</strong><small>${esc(item.inventory_number)} · ${esc(item.location)}</small></div>${badge(item.status)}</div>`).join('')}</div></div>
      </section>
    </div>`;
}

function renderEquipment() {
  const content = document.getElementById('page-content');
  const isStaff = ['admin', 'technician'].includes(state.user.role);
  const actions = isStaff ? '<button class="btn btn-primary" data-action="add-equipment">＋ Добавить оборудование</button>' : '';
  const filtered = state.equipment.filter((item) => {
    const term = state.search.toLowerCase();
    const matchesTerm = !term || `${item.name} ${item.inventory_number} ${item.category} ${item.location}`.toLowerCase().includes(term);
    const matchesCategory = state.category === 'all' || item.category === state.category;
    return matchesTerm && matchesCategory;
  });
  const categories = [...new Set(state.equipment.map((item) => item.category))].sort();
  content.innerHTML = `${heading('Каталог оборудования', 'Выберите лабораторное оборудование и отправьте заявку на нужный период.', actions)}
    <div class="equipment-toolbar"><div class="search-box"><input id="equipment-search" type="search" placeholder="Поиск по названию, инвентарному номеру…" value="${esc(state.search)}"></div><select class="toolbar-select" id="category-filter"><option value="all">Все категории</option>${categories.map((cat) => `<option value="${esc(cat)}" ${state.category === cat ? 'selected' : ''}>${esc(cat)}</option>`).join('')}</select><select class="toolbar-select" id="status-filter"><option value="all">Любой статус</option><option value="available">Доступно</option><option value="issued">Выдано</option><option value="maintenance">На обслуживании</option></select></div>
    <div class="equipment-grid" id="equipment-grid">${renderEquipmentCards(filtered)}</div>`;
  const statusFilter = document.getElementById('status-filter');
  statusFilter.addEventListener('change', () => {
    const status = statusFilter.value;
    const list = state.equipment.filter((item) => {
      const term = state.search.toLowerCase();
      return (!term || `${item.name} ${item.inventory_number} ${item.category} ${item.location}`.toLowerCase().includes(term)) && (state.category === 'all' || item.category === state.category) && (status === 'all' || item.status === status);
    });
    document.getElementById('equipment-grid').innerHTML = renderEquipmentCards(list);
  });
}

function renderEquipmentCards(items) {
  if (!items.length) return `<div class="panel" style="grid-column:1/-1"><div class="empty-state"><div class="empty-icon">⌕</div><strong>Ничего не найдено</strong><span>Попробуйте изменить поисковый запрос или фильтр.</span></div></div>`;
  return items.map((item) => `<article class="equipment-card">
    <div class="equipment-card-top"><div class="equip-icon">${equipmentIcon(item.category)}</div><span class="inventory">${esc(item.inventory_number)}</span></div>
    <h3>${esc(item.name)}</h3><div class="category">${esc(item.category)}</div>
    <div class="equipment-meta">⌖ ${esc(item.location)}</div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">${badge(item.status)}<span class="inventory">ID ${item.id}</span></div>
    <div class="card-actions"><button class="btn btn-primary btn-small" data-action="reserve" data-id="${item.id}" ${item.status === 'maintenance' || item.status === 'retired' ? 'disabled' : ''}>Забронировать</button><button class="btn btn-secondary btn-small" data-action="report-problem" data-id="${item.id}">Проблема</button></div>
  </article>`).join('');
}

function renderReservations() {
  const content = document.getElementById('page-content');
  const isStaff = ['admin', 'technician'].includes(state.user.role);
  const rows = state.reservations.map((r) => {
    const eq = state.equipment.find((e) => e.id === r.equipment_id);
    let actions = '';
    if (isStaff && r.status === 'pending') {
      actions = `<button class="btn btn-success btn-small" data-action="reservation-approve" data-id="${r.id}">Подтвердить</button><button class="btn btn-danger btn-small" data-action="reservation-reject" data-id="${r.id}">Отклонить</button>`;
    } else if (isStaff && r.status === 'approved' && new Date(r.starts_at) <= new Date() && new Date(r.ends_at) > new Date()) {
      actions = `<button class="btn btn-primary btn-small" data-action="reservation-issue" data-id="${r.id}">Выдать</button>`;
    } else if (isStaff && r.status === 'issued') {
      actions = `<button class="btn btn-success btn-small" data-action="reservation-return" data-id="${r.id}">Принять возврат</button>`;
    } else if (!isStaff && ['pending', 'approved'].includes(r.status)) {
      actions = `<button class="btn btn-danger btn-small" data-action="reservation-cancel" data-id="${r.id}">Отменить</button>`;
    }
    return `<tr><td><strong>#${r.id}</strong></td><td><strong>${esc(eq?.name || `Оборудование #${r.equipment_id}`)}</strong><br><span class="inventory">${esc(eq?.inventory_number || '')}</span></td><td>${dateTime(r.starts_at)}<br><span style="color:#9aa5b6">до ${dateTime(r.ends_at)}</span></td><td>${isStaff ? `Пользователь #${r.user_id}` : 'Вы'}</td><td>${badge(r.status)}</td><td><div class="table-actions">${actions || '<span style="color:#aab3c1">—</span>'}</div></td></tr>`;
  }).join('');
  content.innerHTML = `${heading(isStaff ? 'Все бронирования' : 'Мои бронирования', isStaff ? 'Согласование заявок, выдача и контроль возврата оборудования.' : 'История ваших заявок и текущие статусы.')}
    <section class="panel"><div class="panel-head"><div><h3>${state.reservations.length} ${plural(state.reservations.length, 'заявка', 'заявки', 'заявок')}</h3><p>${isStaff ? 'Заявки всех пользователей' : 'Ваши бронирования'}</p></div></div>
    ${rows ? `<div class="table-wrap"><table><thead><tr><th>Номер</th><th>Оборудование</th><th>Период</th><th>${isStaff ? 'Заявитель' : 'Пользователь'}</th><th>Статус</th><th>Действия</th></tr></thead><tbody>${rows}</tbody></table></div>` : `<div class="empty-state"><div class="empty-icon">▤</div><strong>Бронирований пока нет</strong><span>Перейдите в каталог и выберите оборудование.</span></div>`}</section>`;
}

function renderMaintenance() {
  const content = document.getElementById('page-content');
  const isStaff = ['admin', 'technician'].includes(state.user.role);
  const rows = state.maintenance.map((record) => {
    const eq = state.equipment.find((e) => e.id === record.equipment_id);
    let actions = '';
    if (isStaff && record.status === 'open') actions = `<button class="btn btn-primary btn-small" data-action="maintenance-start" data-id="${record.id}">Взять в работу</button><button class="btn btn-success btn-small" data-action="maintenance-resolve" data-id="${record.id}">Закрыть</button>`;
    else if (isStaff && record.status === 'in_progress') actions = `<button class="btn btn-success btn-small" data-action="maintenance-resolve" data-id="${record.id}">Закрыть заявку</button>`;
    return `<tr><td><strong>#${record.id}</strong></td><td><strong>${esc(eq?.name || `Оборудование #${record.equipment_id}`)}</strong><br><span class="inventory">${esc(eq?.inventory_number || '')}</span></td><td>${esc(record.description)}</td><td>${dateTime(record.created_at)}</td><td>${badge(record.status)}</td><td><div class="table-actions">${actions || '<span style="color:#aab3c1">—</span>'}</div></td></tr>`;
  }).join('');
  content.innerHTML = `${heading(isStaff ? 'Техническое обслуживание' : 'Мои сообщения о неисправностях', isStaff ? 'Принимайте обращения, фиксируйте ремонт и возвращайте оборудование в работу.' : 'Сообщайте о неисправностях, чтобы сотрудники лаборатории могли организовать ремонт.')}
    <section class="panel"><div class="panel-head"><div><h3>${state.maintenance.length} ${plural(state.maintenance.length, 'обращение', 'обращения', 'обращений')}</h3><p>${isStaff ? 'Все заявки на обслуживание' : 'Ваши обращения'}</p></div></div>
    ${rows ? `<div class="table-wrap"><table><thead><tr><th>Номер</th><th>Оборудование</th><th>Описание</th><th>Создано</th><th>Статус</th><th>Действия</th></tr></thead><tbody>${rows}</tbody></table></div>` : `<div class="empty-state"><div class="empty-icon">⚙</div><strong>Обращений пока нет</strong><span>Если заметили неисправность, сообщите о ней из каталога оборудования.</span></div>`}</section>`;
}

function renderReports() {
  const content = document.getElementById('page-content');
  const s = state.summary || {};
  const max = Math.max(1, ...state.categories.map((x) => x.count));
  content.innerHTML = `${heading('Отчётность', 'Сводные показатели по использованию оборудования и работе лаборатории.')}
    <div class="stats-grid">${statCard('Всего оборудования', s.equipment_total ?? 0, '▦', 'Включая списанное')}${statCard('Доступно', s.available ?? 0, '✓', 'Готово к бронированию')}${statCard('Выдано', s.issued ?? 0, '↗', 'На руках у пользователей')}${statCard('Просроченные возвраты', s.overdue_returns ?? 0, '◷', 'Требуют контроля')}</div>
    <div class="dashboard-grid"><section class="panel"><div class="panel-head"><div><h3>Оборудование по категориям</h3><p>Количество активных единиц в каждой категории</p></div></div><div class="panel-body"><div class="category-bars">${state.categories.map((x) => `<div class="category-row"><span>${esc(x.category)}</span><strong>${x.count}</strong><div class="bar-track"><div class="bar-fill" style="width:${Math.round(x.count / max * 100)}%"></div></div></div>`).join('')}</div></div></section>
    <section class="panel"><div class="panel-head"><div><h3>Состояние системы</h3><p>Текущая операционная сводка</p></div></div><div class="panel-body"><div class="quick-list">
      <div class="quick-item"><div class="equip-icon">▤</div><div class="quick-copy"><strong>Активные бронирования</strong><small>Новые, подтверждённые и выданные</small></div><strong>${s.active_reservations ?? 0}</strong></div>
      <div class="quick-item"><div class="equip-icon">◷</div><div class="quick-copy"><strong>Ожидают согласования</strong><small>Новые заявки</small></div><strong>${s.pending_reservations ?? 0}</strong></div>
      <div class="quick-item"><div class="equip-icon">⚙</div><div class="quick-copy"><strong>На обслуживании</strong><small>Открытые обращения</small></div><strong>${s.open_maintenance ?? 0}</strong></div>
      <div class="quick-item"><div class="equip-icon">⌁</div><div class="quick-copy"><strong>Списано</strong><small>Исключено из каталога</small></div><strong>${s.retired ?? 0}</strong></div>
    </div></div></section></div>`;
}

function renderUsers() {
  const content = document.getElementById('page-content');
  const rows = state.users.map((user) => `<tr><td><strong>#${user.id}</strong></td><td>${esc(user.email)}</td><td><span class="badge ${user.role === 'admin' ? 'approved' : user.role === 'technician' ? 'pending' : 'available'}">${roleLabels[user.role] || user.role}</span></td><td><select class="toolbar-select" style="min-width:135px;padding:7px" data-role-user="${user.id}"><option value="student" ${user.role === 'student' ? 'selected' : ''}>Студент</option><option value="technician" ${user.role === 'technician' ? 'selected' : ''}>Техник</option><option value="admin" ${user.role === 'admin' ? 'selected' : ''}>Администратор</option></select></td></tr>`).join('');
  content.innerHTML = `${heading('Пользователи', 'Управление учётными записями и правами доступа.')}
    <section class="panel"><div class="panel-head"><div><h3>${state.users.length} пользователей</h3><p>Изменение роли применяется сразу после сохранения.</p></div></div><div class="table-wrap"><table><thead><tr><th>ID</th><th>Электронная почта</th><th>Текущая роль</th><th>Изменить роль</th></tr></thead><tbody>${rows}</tbody></table></div></section>`;
}

function plural(n, one, few, many) {
  const n10 = n % 10, n100 = n % 100;
  if (n10 === 1 && n100 !== 11) return one;
  if (n10 >= 2 && n10 <= 4 && (n100 < 12 || n100 > 14)) return few;
  return many;
}

function openModal(title, body) {
  state.modal = true;
  const wrap = document.createElement('div');
  wrap.className = 'modal-backdrop';
  wrap.id = 'modal-backdrop';
  wrap.innerHTML = `<section class="modal"><div class="modal-head"><h3>${title}</h3><button class="modal-close" type="button" data-action="close-modal">×</button></div><div class="modal-body">${body}</div></section>`;
  document.body.appendChild(wrap);
  wrap.addEventListener('click', (event) => { if (event.target === wrap) closeModal(); });
}

function closeModal() {
  document.getElementById('modal-backdrop')?.remove();
  state.modal = null;
}

function openReservationModal(id) {
  const equipment = state.equipment.find((item) => item.id === id);
  const start = new Date(Date.now() + 24 * 60 * 60 * 1000);
  start.setMinutes(0, 0, 0);
  const end = new Date(start.getTime() + 2 * 60 * 60 * 1000);
  openModal('Новое бронирование', `
    <div class="quick-item" style="padding:0 0 14px;margin-bottom:17px"><div class="equip-icon">${equipmentIcon(equipment?.category)}</div><div class="quick-copy"><strong>${esc(equipment?.name)}</strong><small>${esc(equipment?.inventory_number)} · ${esc(equipment?.location)}</small></div></div>
    <form data-form="reservation">
      <input type="hidden" name="equipment_id" value="${id}">
      <div class="field"><label>Начало бронирования</label><input name="starts_at" type="datetime-local" value="${localDateTimeInput(start)}" required></div>
      <div class="field"><label>Окончание бронирования</label><input name="ends_at" type="datetime-local" value="${localDateTimeInput(end)}" required></div>
      <div class="field"><label>Цель использования</label><textarea name="purpose" minlength="5" required placeholder="Например: выполнение лабораторной работы № 4"></textarea></div>
      <div class="modal-footer"><button type="button" class="btn btn-secondary" data-action="close-modal">Отмена</button><button class="btn btn-primary" type="submit">Отправить заявку</button></div>
    </form>`);
}

function openProblemModal(id) {
  const equipment = state.equipment.find((item) => item.id === id);
  openModal('Сообщить о неисправности', `
    <div class="quick-item" style="padding:0 0 14px;margin-bottom:17px"><div class="equip-icon">${equipmentIcon(equipment?.category)}</div><div class="quick-copy"><strong>${esc(equipment?.name)}</strong><small>${esc(equipment?.inventory_number)}</small></div></div>
    <form data-form="problem"><input type="hidden" name="equipment_id" value="${id}"><div class="field"><label>Что произошло?</label><textarea name="description" minlength="5" required placeholder="Опишите неисправность или проблему с оборудованием"></textarea></div><div class="modal-footer"><button type="button" class="btn btn-secondary" data-action="close-modal">Отмена</button><button class="btn btn-primary" type="submit">Отправить сообщение</button></div></form>`);
}

function openEquipmentModal() {
  openModal('Добавить оборудование', `
    <form data-form="equipment">
      <div class="field"><label>Инвентарный номер</label><input name="inventory_number" required minlength="2" placeholder="LAB-011"></div>
      <div class="field"><label>Название</label><input name="name" required minlength="2" placeholder="Например, Анализатор спектра"></div>
      <div class="field"><label>Категория</label><input name="category" required minlength="2" placeholder="Измерительное оборудование"></div>
      <div class="field"><label>Местоположение</label><input name="location" required minlength="2" placeholder="Лаборатория 204"></div>
      <div class="field"><label>Описание</label><textarea name="description" placeholder="Краткое описание и назначение"></textarea></div>
      <div class="modal-footer"><button type="button" class="btn btn-secondary" data-action="close-modal">Отмена</button><button class="btn btn-primary" type="submit">Сохранить</button></div>
    </form>`);
}

async function refreshAfterAction(message) {
  closeModal();
  toast(message);
  await loadPage();
}

async function handleClick(event) {
  const target = event.target.closest('[data-action], [data-page], [data-demo]');
  if (!target) return;
  if (target.dataset.page) {
    state.page = target.dataset.page;
    document.getElementById('sidebar')?.classList.remove('open');
    showShell();
    return;
  }
  if (target.dataset.demo) {
    const presets = {
      admin: ['admin@labgear.com', 'Admin12345!'],
      technician: ['technician@labgear.com', 'Tech12345!'],
      student: ['student@labgear.com', 'Student123!'],
    };
    document.getElementById('auth-email').value = presets[target.dataset.demo][0];
    document.getElementById('auth-password').value = presets[target.dataset.demo][1];
    return;
  }
  const action = target.dataset.action;
  const id = Number(target.dataset.id);
  try {
    if (action === 'toggle-auth') {
      state.authMode = state.authMode === 'login' ? 'register' : 'login';
      showAuth();
    } else if (action === 'logout') {
      setToken(null); state.user = null; state.page = 'dashboard'; showAuth();
    } else if (action === 'toggle-menu') {
      document.getElementById('sidebar')?.classList.toggle('open');
    } else if (action === 'close-modal') {
      closeModal();
    } else if (action === 'reserve') {
      openReservationModal(id);
    } else if (action === 'report-problem') {
      openProblemModal(id);
    } else if (action === 'add-equipment') {
      openEquipmentModal();
    } else if (action === 'reservation-approve') {
      await api(`/reservations/${id}/approve`, { method: 'POST' }); await refreshAfterAction('Заявка подтверждена.');
    } else if (action === 'reservation-reject') {
      await api(`/reservations/${id}/reject`, { method: 'POST' }); await refreshAfterAction('Заявка отклонена.');
    } else if (action === 'reservation-issue') {
      await api(`/reservations/${id}/issue`, { method: 'POST' }); await refreshAfterAction('Оборудование выдано.');
    } else if (action === 'reservation-return') {
      await api(`/reservations/${id}/return`, { method: 'POST' }); await refreshAfterAction('Возврат оборудования зарегистрирован.');
    } else if (action === 'reservation-cancel') {
      if (!confirm('Отменить это бронирование?')) return;
      await api(`/reservations/${id}/cancel`, { method: 'POST' }); await refreshAfterAction('Бронирование отменено.');
    } else if (action === 'maintenance-start') {
      await api(`/maintenance/${id}/start`, { method: 'POST' }); await refreshAfterAction('Заявка взята в работу.');
    } else if (action === 'maintenance-resolve') {
      await api(`/maintenance/${id}/resolve`, { method: 'POST' }); await refreshAfterAction('Заявка закрыта.');
    }
  } catch (error) { toast(error.message, 'error'); }
}

async function handleSubmit(event) {
  const form = event.target.closest('form');
  if (!form) return;
  if (form.id === 'auth-form') {
    event.preventDefault();
    const data = new FormData(form);
    const payload = { email: data.get('email'), password: data.get('password') };
    try {
      if (state.authMode === 'register') {
        await api('/auth/register', { method: 'POST', body: JSON.stringify(payload) });
        toast('Аккаунт создан. Теперь войдите в систему.');
        state.authMode = 'login'; showAuth();
        document.getElementById('auth-email').value = payload.email;
      } else {
        const result = await api('/auth/login', { method: 'POST', body: JSON.stringify(payload) });
        setToken(result.access_token);
        state.user = result.user;
        state.page = 'dashboard';
        showShell();
      }
    } catch (error) { toast(error.message, 'error'); }
    return;
  }

  const formType = form.dataset.form;
  if (!formType) return;
  event.preventDefault();
  const data = new FormData(form);
  try {
    if (formType === 'reservation') {
      const startsAt = new Date(data.get('starts_at'));
      const endsAt = new Date(data.get('ends_at'));
      if (Number.isNaN(startsAt.getTime()) || Number.isNaN(endsAt.getTime()) || endsAt <= startsAt) throw new Error('Проверьте даты бронирования.');
      await api('/reservations', { method: 'POST', body: JSON.stringify({
        equipment_id: Number(data.get('equipment_id')),
        starts_at: startsAt.toISOString(),
        ends_at: endsAt.toISOString(),
        purpose: data.get('purpose'),
      }) });
      state.page = 'reservations'; showShell(); toast('Заявка отправлена на согласование.');
    } else if (formType === 'problem') {
      await api('/maintenance', { method: 'POST', body: JSON.stringify({ equipment_id: Number(data.get('equipment_id')), description: data.get('description') }) });
      state.page = 'maintenance'; showShell(); toast('Сообщение о неисправности отправлено.');
    } else if (formType === 'equipment') {
      await api('/equipment', { method: 'POST', body: JSON.stringify({
        inventory_number: data.get('inventory_number'), name: data.get('name'), category: data.get('category'),
        location: data.get('location'), description: data.get('description') || null,
      }) });
      state.page = 'equipment'; showShell(); toast('Оборудование добавлено в каталог.');
    }
  } catch (error) { toast(error.message, 'error'); }
}

function handleInput(event) {
  if (event.target.id === 'equipment-search') {
    state.search = event.target.value;
    const status = document.getElementById('status-filter')?.value || 'all';
    const list = state.equipment.filter((item) => {
      const term = state.search.toLowerCase();
      return (!term || `${item.name} ${item.inventory_number} ${item.category} ${item.location}`.toLowerCase().includes(term)) && (state.category === 'all' || item.category === state.category) && (status === 'all' || item.status === status);
    });
    const grid = document.getElementById('equipment-grid');
    if (grid) grid.innerHTML = renderEquipmentCards(list);
  }
}

async function handleChange(event) {
  if (event.target.id === 'category-filter') {
    state.category = event.target.value;
    renderEquipment();
  } else if (event.target.matches('[data-role-user]')) {
    const userId = event.target.dataset.roleUser;
    try {
      await api(`/users/${userId}/role`, { method: 'PATCH', body: JSON.stringify({ role: event.target.value }) });
      toast('Роль пользователя обновлена.');
      state.users = await api('/users');
      renderUsers();
    } catch (error) { toast(error.message, 'error'); renderUsers(); }
  }
}

async function boot() {
  document.addEventListener('click', handleClick);
  document.addEventListener('submit', handleSubmit);
  document.addEventListener('input', handleInput);
  document.addEventListener('change', handleChange);
  if (!state.token) return showAuth();
  try {
    state.user = await api('/auth/me');
    showShell();
  } catch {
    setToken(null);
    showAuth();
  }
}

boot();
