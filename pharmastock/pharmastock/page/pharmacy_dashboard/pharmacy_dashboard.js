frappe.pages["pharmacy-dashboard"].on_page_load = function (wrapper) {
	// Create the page
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Pharmastock Dashboard",
		single_column: true,
	});

	// ------------------------------------------------------------------
	// Add buttons to the page toolbar using `page.add_button`
	// ------------------------------------------------------------------

	// Refresh button
	page.add_button(
		__("Refresh"),
		function () {
			load_dashboard_data();
		},
		{ icon: "fa fa-refresh" },
	);

	// Quick action: New Stock In
	page.add_button(
		__("New Stock In"),
		function () {
			frappe.new_doc("Stock In");
		},
		{ icon: "fa fa-arrow-down" },
	);

	// Quick action: New Stock Out
	page.add_button(
		__("New Stock Out"),
		function () {
			frappe.new_doc("Stock Out");
		},
		{ icon: "fa fa-arrow-up" },
	);

	// Build the dashboard HTML
	build_dashboard(page);

	// Load initial data
	load_dashboard_data();
};

// ------------------------------------------------------------------
// Build the HTML structure
// ------------------------------------------------------------------
function build_dashboard(page) {
	const html = [
		'<div class="pharmastock-dashboard" style="padding: 20px;">',

		// Filters row
		'<div class="row" style="margin-bottom: 20px;">',
		'<div class="col-md-4">',
		"<label>Category</label>",
		'<select id="filter-category" class="form-control">',
		'<option value="">All Categories</option>',
		"</select>",
		"</div>",
		'<div class="col-md-4">',
		"<label>Stock Status</label>",
		'<select id="filter-status" class="form-control">',
		'<option value="">All</option>',
		'<option value="Low">Low</option>',
		'<option value="Out of Stock">Out of Stock</option>',
		'<option value="Sufficient">Sufficient</option>',
		"</select>",
		"</div>",
		'<div class="col-md-4">',
		"<label>Last updated:</label>",
		'<div id="last-updated" style="margin-top: 8px; color: #6b7280;">Never</div>',
		"</div>",
		"</div>",

		// KPI Cards
		'<div class="row" style="margin-bottom: 20px;">',
		'<div class="col-md-3">',
		'<div class="card" style="border-left: 4px solid #4a90e2;">',
		'<div class="card-body">',
		'<div style="color: #6b7280;">Total Medicines</div>',
		'<h2 id="total-medicines">0</h2>',
		"</div></div></div>",

		'<div class="col-md-3">',
		'<div class="card" style="border-left: 4px solid #28a745;">',
		'<div class="card-body">',
		'<div style="color: #6b7280;">In Stock</div>',
		'<h2 id="in-stock">0</h2>',
		"</div></div></div>",

		'<div class="col-md-3">',
		'<div class="card" style="border-left: 4px solid #ffc107;">',
		'<div class="card-body">',
		'<div style="color: #6b7280;">Low Stock</div>',
		'<h2 id="low-stock">0</h2>',
		"</div></div></div>",

		'<div class="col-md-3">',
		'<div class="card" style="border-left: 4px solid #dc3545;">',
		'<div class="card-body">',
		'<div style="color: #6b7280;">Total Stock Value</div>',
		'<h2 id="stock-value">0</h2>',
		"</div></div></div>",
		"</div>",

		// Charts
		'<div class="row" style="margin-bottom: 20px;">',
		'<div class="col-md-6">',
		'<div class="card">',
		'<div class="card-header"><strong>Stock by Category</strong></div>',
		'<div class="card-body"><div id="category-chart"></div></div>',
		"</div></div>",
		'<div class="col-md-6">',
		'<div class="card">',
		'<div class="card-header"><strong>Expiry Status</strong></div>',
		'<div class="card-body"><div id="expiry-chart"></div></div>',
		"</div></div>",
		"</div>",

		// Low Stock Table
		'<div class="row">',
		'<div class="col-md-12">',
		'<div class="card">',
		'<div class="card-header"><strong>⚠️ Low Stock Items</strong></div>',
		'<div class="card-body">',
		'<div class="table-responsive">',
		'<table class="table table-bordered table-hover">',
		"<thead><tr><th>Medicine</th><th>Category</th><th>Current Stock</th><th>Reorder Level</th><th>Status</th></tr></thead>",
		'<tbody id="low-stock-body"></tbody>',
		"</table></div></div></div></div>",
		"</div></div>",
	].join("");

	$(page.main).html(html);

	// Populate category filter from server
	frappe.call({
		method: "pharmastock.pharmastock.page.pharmacy_dashboard.pharmacy_dashboard.get_categories",
		callback: function (r) {
			if (r.message) {
				let select = $("#filter-category");
				r.message.forEach((cat) => {
					select.append(`<option value="${cat.name}">${cat.name}</option>`);
				});
			}
		},
	});

	// Bind filter change events
	$("#filter-category, #filter-status").on("change", function () {
		load_dashboard_data();
	});
}

// ------------------------------------------------------------------
// Load data from server
// ------------------------------------------------------------------
function load_dashboard_data() {
	// Disable refresh button and show spinner
	let refresh_btn = $('.page-head .page-actions .btn:contains("Refresh")');
	refresh_btn.prop("disabled", true).html('<i class="fa fa-spinner fa-spin"></i> Loading...');

	let filters = {
		category: $("#filter-category").val() || "",
		status: $("#filter-status").val() || "",
	};

	frappe.call({
		method: "pharmastock.pharmastock.page.pharmacy_dashboard.pharmacy_dashboard.get_dashboard_data",
		args: { filters: filters },
		callback: function (response) {
			if (response.message) {
				update_dashboard(response.message);
				$("#last-updated").text(new Date().toLocaleString());
			}
			// Restore button
			refresh_btn.prop("disabled", false).html('<i class="fa fa-refresh"></i> Refresh');
		},
		error: function (error) {
			frappe.msgprint({
				title: "Dashboard Error",
				message: "Unable to load dashboard data.",
				indicator: "red",
			});
			refresh_btn.prop("disabled", false).html('<i class="fa fa-refresh"></i> Refresh');
		},
	});
}

// ------------------------------------------------------------------
// Update UI with received data
// ------------------------------------------------------------------
function update_dashboard(data) {
	$("#total-medicines").text(data.total_medicines || 0);
	$("#in-stock").text(data.in_stock || 0);
	$("#low-stock").text(data.low_stock || 0);
	$("#stock-value").text(data.total_stock_value ? data.total_stock_value.toFixed(2) : "0.00");

	update_low_stock_table(data.low_stock_items || []);
	create_category_chart(data.category_data);
	create_expiry_chart(data.expiry_data);
}

// ------------------------------------------------------------------
// Update the low stock table (rows clickable)
// ------------------------------------------------------------------
function update_low_stock_table(items) {
	const tbody = $("#low-stock-body");
	tbody.empty();

	if (!items.length) {
		tbody.append(
			'<tr><td colspan="5" class="text-center text-muted">No low stock medicines.</td></tr>',
		);
		return;
	}

	items.forEach(function (item) {
		let row = $("<tr>").css("cursor", "pointer");
		row.append(`<td>${escape_html(item.medicine_name || "")}</td>`);
		row.append(`<td>${escape_html(item.category || "Uncategorized")}</td>`);
		row.append(`<td>${item.current_stock || 0}</td>`);
		row.append(`<td>${item.reorder_level || 0}</td>`);
		row.append(`<td><span class="badge bg-warning text-dark">Low</span></td>`);

		// Click to open Medicine record
		row.on("click", function () {
			if (item.name) {
				frappe.set_route("Form", "Medicine", item.name);
			}
		});

		tbody.append(row);
	});
}

// ------------------------------------------------------------------
// Create charts using frappe.Chart
// ------------------------------------------------------------------
function create_category_chart(data) {
	if (!data || !data.labels || !data.values) return;
	$("#category-chart").empty();
	new frappe.Chart("#category-chart", {
		title: "Stock by Category",
		data: {
			labels: data.labels,
			datasets: [{ name: "Stock", values: data.values }],
		},
		type: "bar",
		height: 300,
		colors: ["#4a90e2"],
	});
}

function create_expiry_chart(data) {
	if (!data || !data.labels || !data.values) return;
	$("#expiry-chart").empty();
	new frappe.Chart("#expiry-chart", {
		title: "Expiry Status",
		data: {
			labels: data.labels,
			datasets: [{ name: "Quantity", values: data.values }],
		},
		type: "donut",
		height: 300,
		colors: ["#28a745", "#ffc107", "#dc3545", "#6c757d"],
		// Spacing for legends
		legend: {
			position: "right",
		},
	});
}

// ------------------------------------------------------------------
// Utility: escape HTML to prevent XSS
// ------------------------------------------------------------------
function escape_html(value) {
	return $("<div>").text(value).html();
}
