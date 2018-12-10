-- Bring all reports from PBI server
SELECT
	ItemID as report_itemid,
	Name as report_name,
	left([Path],LEN([Path])-LEN(Name)-1) as report_folder,
	ISNULL(Description,'No description') as report_description,
	ParentID as report_parentid
FROM
	dbo.[catalog]
where
	[Type] = 13;
