-- Bring all reports from PBI server
select
	*
from
	dbo.[Catalog]
where
	[Type] = 13;
