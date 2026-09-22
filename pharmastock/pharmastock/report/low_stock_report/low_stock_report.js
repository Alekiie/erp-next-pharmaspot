// Copyright (c) 2026, Alexander Maina and contributors
// For license information, please see license.txt

frappe.query_reports["Low Stock Report"] = {
	filters: [
		{
			fieldname: "category",
			label: __("Category"),
			fieldtype: "Link",
			options: "Medicine Category",
		},
		{
			fieldname: "status",
			label: __("Stock Status"),
			fieldtype: "Select",
			options: ["All", "Low", "Sufficient", "Out of Stock"],
		},
	],

	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname == "status") {
			if (value == "Low") {
				return '<span style="color: red; font-weight: bold;">' + value + "</span>";
			} else if (value == "Out of Stock") {
				return '<span style="color: darkred; font-weight: bold;">' + value + "</span>";
			} else if (value == "Sufficient") {
				return '<span style="color: green;">' + value + "</span>";
			}
		}

		if (column.fieldname == "current_stock") {
			if (data && data.reorder_level && value <= data.reorder_level) {
				return '<span style="color: red; font-weight: bold;">' + value + "</span>";
			}
		}

		return value;
	},
};
