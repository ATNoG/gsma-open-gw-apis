---
title: System Requirements 
description: Functional and Non-Functional Requirements
sidebar_position: 4
---

# System Requirements

## Functional Requirements

**Location Services**:
* The system must allow the creation of subscriptions so that the API clients receive notifications when entering or leaving a defined area.
* The system must allow obtaining the location of a device, described as either a circle (center coordinates and radius) or a simple polygon (list of coordinates).
* The system must allow verifying whether a device is within a certain area. If the area is outside the operator’s coverage or invalid, the system must return the appropriate errors.
* The system must provide an estimate of the population density in a specified area.

**Communication Quality**:
* The system must enable the exchange of relevant information to assist in decision-making related to network APIs.
* The system must allow developers to query the network about the likelihood of meeting connectivity requirements during a session.
* The system must allow developers to define different QoS (Quality of Service) levels on customer APs, depending on their bandwidth needs.
* The system must provide existing QoS profiles within a network, returning relevant information about them.
* The system must allow the assignment of QoS profiles to a device. The network will apply the QoS profile to the device’s traffic whenever it is connected until the provisioning is removed.

**Fraud Prevention**:
* The system must allow the verification of a phone number via OTP (One-Time Password) validation.

**Device Information Retrieval**:
* The system must allow verification of whether a specific device is available on the network.
* The system must allow an API subscriber to be notified if there is a change in the availability of a specific device.
* The system must allow verification of whether a specific device is in a roaming state. If true, it must return existing information about the country.
* The system must allow an API subscriber to be notified if there is any change in a device’s roaming status.

## Non-Functional Requirements

**Performance and Latency**:
* The system must maintain consistent response times as the user base or data volume increases.
* The system must handle a growing number of requests efficiently.

**Scalability**:
* The system must support a high volume of requests and connected devices.
* The system must scale horizontally and/or vertically according to demand.

**Availability and Reliability**:
* The system must ensure high availability levels (e.g., SLA of 99.9% uptime).
* The system must demonstrate a high level of reliability (i.e., 99.9999% reliability).
* The system must have redundancy and fault tolerance mechanisms to ensure continuous operation even in adverse conditions.

**Interoperability**:
* The system must be compatible with various network operators, ensuring that the APIs integrate with different network infrastructures and promote service universality.
* The system must follow open standards and best practices to promote interoperability and universal acceptance among different systems and technologies.

**Maintainability and Extensibility**:
* The system must have a modular architecture, allowing it to be divided into independent components, making updates and fixes easier without disrupting overall functionality.
* The system must include detailed documentation and manuals to help developers understand and maintain it efficiently.
* The system must have clean and readable code, following best practices to ensure ease of understanding and modification, reducing the likelihood of errors.
* The system must allow flexible updates, enabling the implementation of new features or improvements without requiring extensive code rewrites.

**Usability**:
* The system must return errors following a defined standard to facilitate API integration.
* The system must return only relevant information to the developer, abstracting complex network details.
