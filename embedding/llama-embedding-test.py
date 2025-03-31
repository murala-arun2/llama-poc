# import ollama
# client = ollama.Client(model="llama3.2")

from huggingface_hub import login, whoami
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load model and tokenizer
# model_name = "meta-llama/Llama-3.2-3B"
# model_name = "bigcode/starcoder2-3b"
model_name = "microsoft/codebert-base"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="cuda",
    torch_dtype="auto",
    trust_remote_code=True,
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# with open("apache-hertzbeat-output.puml", "r") as f:
#     text = f.read()
#     print("words in class diagram :", len(text.split()))
#     client.generate()


prompt = "explain code flow to AuthorityAuthorizationManager.check() method"
# prompt = """
# Context: 
# You are a java developer and you are given a class diagram of project in plantuml syntax.

# Class Diagram:

# `@startuml
# package org {
# package apache {
# package hertzbeat {
# package manager {
# package component {
# package listener {
# class TimeZoneListener    {
#   objectMapper : ObjectMapper
#   onEvent(event : SystemConfigChangeEvent) : void
# }
# TimeZoneListener::onEvent --> org.apache.hertzbeat.common.support.event.SystemConfigChangeEvent::getSource : event.getSource() 
# TimeZoneListener::onEvent --> com.fasterxml.jackson.databind.ObjectMapper::setTimeZone : objectMapper.setTimeZone(TimeZone.getDefault()).setDateFormat(simpleDateFormat) 
# TimeZoneListener::onEvent --> com.fasterxml.jackson.databind.ObjectMapper::setTimeZone : objectMapper.setTimeZone(TimeZone.getDefault()) 
# }
# package sd {
# class ServiceDiscoveryWorker  implements org.springframework.beans.factory.InitializingBean  {
#   monitorService : MonitorService
#   paramDao : ParamDao
#   monitorDao : MonitorDao
#   monitorBindDao : MonitorBindDao
#   collectorMonitorBindDao : CollectorMonitorBindDao
#   dataQueue : CommonDataQueue
#   workerPool : ManagerWorkerPool
#   ServiceDiscoveryWorker(monitorService : MonitorService, paramDao : ParamDao, monitorDao : MonitorDao, monitorBindDao : MonitorBindDao, collectorMonitorBindDao : CollectorMonitorBindDao, dataQueue : CommonDataQueue, workerPool : ManagerWorkerPool) : None
#   afterPropertiesSet() : void
# }
# ServiceDiscoveryWorker::afterPropertiesSet --> org.apache.hertzbeat.manager.scheduler.ManagerWorkerPool::executeJob : workerPool.executeJob(newSdUpdateTask()) 
# class SdUpdateTask    {
#   run() : void
# }
# }
# package status {
# class CalculateStatus    {
#   DEFAULT_CALCULATE_INTERVAL_TIME : int
#   statusPageOrgDao : StatusPageOrgDao
#   statusPageComponentDao : StatusPageComponentDao
#   statusPageHistoryDao : StatusPageHistoryDao
#   monitorDao : MonitorDao
#   intervals : int
#   CalculateStatus(statusPageOrgDao : StatusPageOrgDao, statusPageComponentDao : StatusPageComponentDao, statusProperties : StatusProperties, statusPageHistoryDao : StatusPageHistoryDao, monitorDao : MonitorDao) : None
#   startCalculate() : void
#   startCombineHistory() : void
#   getCalculateStatusIntervals() : int
# }
# CalculateStatus::startCalculate --> org.apache.hertzbeat.manager.dao.StatusPageOrgDao::findAll : statusPageOrgDao.findAll() 
# CalculateStatus::startCalculate --> org.apache.hertzbeat.manager.dao.StatusPageComponentDao::findByOrgId : statusPageComponentDao.findByOrgId(orgId) 
# CalculateStatus::startCalculate --> org.apache.hertzbeat.manager.dao.MonitorDao::findAll : monitorDao.findAll(specification) 
# CalculateStatus::startCalculate --> org.apache.hertzbeat.manager.dao.StatusPageComponentDao::save : statusPageComponentDao.save(component) 
# CalculateStatus::startCalculate --> org.apache.hertzbeat.manager.dao.StatusPageHistoryDao::save : statusPageHistoryDao.save(statusPageHistory) 
# CalculateStatus::startCalculate --> org.apache.hertzbeat.manager.dao.StatusPageOrgDao::save : statusPageOrgDao.save(statusPageOrg) 
# CalculateStatus::startCombineHistory --> org.apache.hertzbeat.manager.dao.StatusPageHistoryDao::findStatusPageHistoriesByTimestampBetween : statusPageHistoryDao.findStatusPageHistoriesByTimestampBetween(preNightTimestamp,midnightTimestamp) 
# CalculateStatus::startCombineHistory --> org.apache.hertzbeat.manager.dao.StatusPageHistoryDao::deleteAll : statusPageHistoryDao.deleteAll(statusPageHistoryList) 
# CalculateStatus::startCombineHistory --> org.apache.hertzbeat.manager.dao.StatusPageHistoryDao::save : statusPageHistoryDao.save(history) 
# }
# }
# """

# Tokenize the input prompt
input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to("cuda")
# print tokens
for id in input_ids[0]:
   print(tokenizer.decode(id))

