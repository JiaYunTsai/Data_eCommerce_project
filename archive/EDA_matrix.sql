--purchase_data
WITH 
PURCHASE_DATA AS
  (
    SELECT UnitPrice,Qty,FullvisitorId,EventTime,UnitPrice*Qty AS REVENUE
    FROM `lustrous-setup-386509.BehaviorData.BehaviorData`
    WHERE Behavior='purchase'
  ),
SESSION_DATA AS
  (
    SELECT FullvisitorId,COUNT(DISTINCT HitTime) AS SESSION,
    FROM `lustrous-setup-386509.BehaviorData.BehaviorData`
    GROUP BY FullvisitorId
  )
SELECT SUM(PURCHASE_DATA.REVENUE) AS TOTAL_REVENUE,
      COUNT(DISTINCT PURCHASE_DATA.FullvisitorId) AS MEMBER_PURCHASE,
      COUNT(DISTINCT PURCHASE_DATA.EventTime) AS ORDERS,
      SUM(PURCHASE_DATA.REVENUE)/COUNT(DISTINCT PURCHASE_DATA.EventTime) AS AOV,
#      SUM(SESSION_DATA.SESSION) AS TOTAL_SESSION,
#      COUNT(DISTINCT PURCHASE_DATA.EventTime)/SUM(SESSION_DATA.SESSION)  AS CR
FROM PURCHASE_DATA;

SELECT SUM(A.SESSION) AS TOTAL_SESSIONS,
       AVG(A.SESSION) AS AVG_SESSION       
FROM
(
SELECT FullvisitorId,COUNT(DISTINCT HitTime) AS SESSION,
FROM `lustrous-setup-386509.BehaviorData.BehaviorData`
GROUP BY FullvisitorId
)A
--member_data
SELECT COUNT(DISTINCT FullvisitorId) AS MEMBERS,
FROM `lustrous-setup-386509.BehaviorData.BehaviorData`
