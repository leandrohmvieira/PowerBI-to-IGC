-- Bring all folders from PBI server
SELECT
	ItemID as itemid,
	COALESCE(NULLIF(Name,''),'root') as name,
	ParentID as parentid,
	ISNULL(Description,'No description') as description
FROM
	dbo.[catalog]
where
	[Type] = 1;
