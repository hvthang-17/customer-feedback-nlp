const $ = s => document.querySelector(s);

const names = {
    sales: 'Kinh doanh',
    customer_service: 'Chăm sóc khách hàng',
    technical: 'Kỹ thuật',
    finance_accounting: 'Kế toán / Tài chính',
    human_resources: 'Nhân sự'
};

async function api(url, options) {
    const r = await fetch(url, options);

    if (!r.ok)
        throw new Error(await r.text());

    return r.json();
}

function row(e, review = false) {
    const dep =
        names[e.route_department || e.predicted_department] ||
        'Cần kiểm duyệt';

    if (review)
        return `<tr>
            <td>
                <b>${e.subject}</b>
                <small>${e.sender}</small>
            </td>
            <td>${names[e.predicted_department]}</td>
            <td class="confidence low">
                ${Math.round(e.confidence * 100)}%
            </td>
            <td>
                <button onclick="approve(${e.id},'${e.predicted_department}')">
                    Chấp nhận
                </button>
            </td>
        </tr>`;

    return `<tr>
        <td><b>${e.subject}</b></td>
        <td>${e.sender}</td>
        <td>${dep}</td>
        <td>
            <span class="badge">${e.status}</span>
        </td>
    </tr>`;
}

async function load() {
    const [d, review, emails, experiments] = await Promise.all([
        api('/api/dashboard'),
        api('/api/review-queue'),
        api('/api/emails'),
        api('/api/experiments')
    ]);

    $('#total').textContent = d.total;
    $('#auto').textContent = d.auto_routed;
    $('#reviewMetric').textContent = d.needs_review;
    $('#correction').textContent = d.correction_rate + '%';
    $('#reviewCount').textContent = review.length;

    const max = Math.max(
        ...Object.values(d.distribution),
        1
    );

    $('#distribution').innerHTML = Object.entries(d.distribution)
        .map(
            ([k, v]) =>
                `<div class="barrow">
                    <span>${names[k]}</span>
                    <div class="track">
                        <div class="fill" style="width:${v / max * 100}%"></div>
                    </div>
                    <b>${v}</b>
                </div>`
        )
        .join('');

    $('#reviewRows').innerHTML = review.length
        ? review.map(x => row(x, true)).join('')
        : '<tr><td colspan="4">Không có email cần kiểm duyệt.</td></tr>';

    renderEmails(emails);

    $('#experimentRows').innerHTML = experiments
        .map(
            x =>
                `<tr>
                    <td>${x.model}</td>
                    <td>${(x.f1_macro * 100).toFixed(0)}%</td>
                    <td>${(x.accuracy * 100).toFixed(0)}%</td>
                    <td>${x.seed}</td>
                </tr>`
        )
        .join('');
}

let all = [];

function renderEmails(items) {
    all = items;
    $('#emailRows').innerHTML = items.map(x => row(x)).join('');
}

window.approve = async (id, department) => {
    await api(`/api/emails/${id}/review`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            department,
            reason: 'Đã xác nhận dự đoán'
        })
    });

    load();
};

$('#openModal').onclick = () => $('#modal').showModal();

$('#closeModal').onclick = () => $('#modal').close();

$('#emailForm').onsubmit = async e => {
    e.preventDefault();

    const f = new FormData(e.target);

    try {
        const result = await api('/api/emails', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(Object.fromEntries(f))
        });

        $('#formMessage').textContent =
            `Đã nạp: ${result.department_name} (${Math.round(result.confidence * 100)}%)`;

        load();
    } catch {
        $('#formMessage').textContent =
            'Không thể nạp email. Kiểm tra dữ liệu.';
    }
};

$('#statusFilter').onchange = e =>
    renderEmails(
        e.target.value
            ? all.filter(x => x.status === e.target.value)
            : all
    );

load();