-- Bring all reports from PBI server
SELECT
	Name,
	'server' as server,
	left([Path],LEN([Path])-LEN(Name)-1) as folder,
	'No description' as description
FROM
	dbo.[catalog]
where
	[Type] = 13;

select
	'banana' as penis
from
	dbo.[Catalog];
