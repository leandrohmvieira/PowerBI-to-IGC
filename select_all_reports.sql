-- Bring all reports from PBI server
SELECT
	ItemID as itemid,
	Name as name,
	'server' as server,
	left([Path],LEN([Path])-LEN(Name)-1) as folder,
	ISNULL(Description,'No description') as description
FROM
	dbo.[catalog]
where
	[Type] = 13;
