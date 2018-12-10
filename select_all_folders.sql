-- Bring all folders from PBI server
SELECT
	ItemID as folder_itemid,
	COALESCE(NULLIF(Name,''),'root') as folder_name,
	ParentID as folder_parentid,
	ISNULL(Description,'No description') as folder_description
FROM
	dbo.[catalog]
where
	[Type] = 1;
